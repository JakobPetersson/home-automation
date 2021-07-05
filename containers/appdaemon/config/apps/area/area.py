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

        self.light_state = {}
        await self.update_light_state({
            "on": False,
            "kelvin": 3500,
            "brightness_pct": 100
        }, datetime.datetime.now(datetime.timezone.utc))

    async def init_sub_areas(self):
        sub_areas_name = self.args.get("sub_areas") or []
        self.sub_areas = []
        for area_name in sub_areas_name:
            sub_area = await self.get_app(area_name)
            if not sub_area:
                self.log("Sub area not initialized, {}".format(area_name))
                self.terminate()
            self.sub_areas.append(sub_area)

    #
    # Services (Called from  other apps)
    #

    async def service_manual(self, cmd_name, time_fired):
        await self._service(cmd_name, time_fired)

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
