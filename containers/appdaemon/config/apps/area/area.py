import hassapi as hass
import asyncio
import datetime


class Area(hass.Hass):

    async def initialize(self):

        self.area_id = self.args.get("area_id")

        self.last_update = datetime.datetime.now(datetime.timezone.utc)
        self.task_1 = None
        self.waiting = False

        await self.init_sub_areas()
        await self.init_area_lights()

        self.light_state = {}
        await self.update_light_state({
            "on": False,
            "kelvin": 3500,
            "brightness_pct": 100
        }, datetime.datetime.now(datetime.timezone.utc))


    async def init_area_lights(self):
        if not self.area_id:
            return

        all_state = await self.get_state()

        for entity_id in all_state:
            device_name, entity_name = await self.split_entity(entity_id)

            # Require entity name to start with light.<area_id>*
            if device_name != "light" or not entity_name.startswith(self.area_id):
                continue

            self.log("Area light {}".format(entity_id))
            await self.init_light(all_state[entity_id])


    async def init_light(self, entity):
        pass
#        event_listen_handle = await self.listen_state(
#            self.light_state_cb,
#            entity["entity_id"],
#            attribute="all"
#        )


    async def light_state_cb(self, entity, attribute, old, new, kwargs):
        pass
        self.log("light_state_cb")
        self.log("Entity: {}".format(entity))
        self.log("Attr: {}".format(attribute))
        self.log("Old: {}".format(old))
        self.log("New: {}".format(new))
        

    #
    # Init sub areas
    #
    async def init_sub_areas(self):
        # Initialize local variable to keep references to sub areas
        self.sub_areas = []

        # Initiaize local variable to keep reference to super area
        self.super_area = None
        self.super_area_name = None

        # Get argument for sub areas
        sub_areas_names = self.args.get("sub_areas") or []

        # Loop over all sub area names and get references to the apps
        for area_name in sub_areas_names:
            sub_area = await self.get_app(area_name)
            if not sub_area:
                # Fail to initalize if sub area is not found
                self.log("Failed to intialize sub area: {}".format(area_name))
                self.terminate()
            
            # Store reference to sub area
            self.sub_areas.append(sub_area)

            # Register ourself as parent to sub area
            await sub_area.service_register_super_area(self.name)

    #
    # Services (Called from  other apps)
    #

    #
    # Register as super area to this area.
    # Can only be called once. (Single super area, tree structure)
    #
    async def service_register_super_area(self, super_area_name):
        if self.super_area != None:
            # Do not allow multiple calls to register super area
            self.log("Register super area has already been called, now called with {}".format(area_name))
            self.terminate()

        self.super_area_name = super_area_name
        self.super_area = await self.get_app(super_area_name)
        
        if not self.super_area:
            # Failed to initalize super area
            self.log("Failed to initialized super area: {}".format(super_area_name))
            self.terminate()

    #
    # Send manual command to super area.
    # Will bubble up to super area until it reaches the top.
    #
    async def service_super_manual(self, cmd_name, time_fired):
        if self.super_area != None:
            # Forward to super area
            await self.super_area.service_super_manual(cmd_name, time_fired)
        else:
            # We are the topmost area
            await self._service(cmd_name, time_fired)

    #
    # Send automated command to super area.
    # Will bubble up to super area until it reaches the top.
    #
    async def service_super_automated(self, cmd_name, time_fired):
        if self.super_area != None:
            # Forward to super area
            await self.super_area.service_super_automated(cmd_name, time_fired)
        else:
            # We are the topmost area
            await self._service(cmd_name, time_fired)

    #
    # Send manual command to area.
    # Will affect sub areas as well.
    #
    async def service_manual(self, cmd_name, time_fired):
        await self._service(cmd_name, time_fired)

    #
    # Send automated command to area.
    # Will affect sub areas as well.
    #
    async def service_automated(self, cmd_name, time_fired):
        await self._service(cmd_name, time_fired)

    #
    #
    #

    async def _service(self, cmd_name, time_fired):
        if cmd_name == "on":
            await self.update_light_state({
                "on": True
            }, time_fired)
        elif cmd_name == "off":
            await self.update_light_state({
                "on": False
            }, time_fired)
        elif cmd_name == "dim_up":
            await self.update_light_state({
                "on": True,
                "brightness_pct": min(100, self.light_state["brightness_pct"] + 5)
            }, time_fired)
        elif cmd_name == "dim_down":
            if self.light_state["on"]:
                await self.update_light_state({
                    "brightness_pct": max(1, self.light_state["brightness_pct"] - 5)
                }, time_fired)

    #
    #
    #

    async def update_light_state(self, light_state_update, time_fired, update_physical_lights=True):
        # self.log(time_fired)

        # Perform actions on this area if state is changed
        if time_fired < self.last_update:
            self.log("Old update!")
            return

        # Get new state by applying state update to current state
        new_state = {**self.light_state, **light_state_update}

        # Update state to new state
        self.last_update = time_fired
        self.light_state = new_state
        # self.log("Updated: {}".format(self.light_state))

        # Propagate light state to all sub areas
        for sub_area in self.sub_areas:
            await self.create_task(sub_area.update_light_state(self.light_state, time_fired, False))

        if update_physical_lights:
            if self.task_1 and not self.task_1.done():
                if self.waiting:
                    self.log("Skipping")
                    return
                else:
                    self.waiting = True
                    self.log("Waiting")
                    await asyncio.wait_for(self.task_1, None)
                    self.waiting = False

            self.task_1 = await self.create_task(self._update_area())

    #
    # Get the area id of this area and all its sub areas
    #
    async def get_area_ids(self):
        area_ids = []

        if self.area_id:
            area_ids.append(self.area_id)

        for sub_area in self.sub_areas:
            area_ids.extend(await sub_area.get_area_ids())

        return area_ids

    #
    # Call HASS to update lights in area
    #
    async def _update_area(self):
        area_ids = await self.get_area_ids()

        if self.light_state["on"]:
            await self.call_service(
                "light/turn_on",
                area_id=area_ids,
                kelvin=self.light_state["kelvin"],
                brightness_pct=self.light_state["brightness_pct"]
            )
        else:
            await self.call_service(
                "light/turn_off",
                area_id=area_ids
            )

    async def terminate(self):
        pass
