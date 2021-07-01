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

        self.state = {}
        await self.update(datetime.datetime.now(datetime.timezone.utc), {
            "on": False,
            "kelvin": 3500,
            "brightness_pct": 100
        })

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

    async def service_manual(self, time_fired, cmd_name):
        await self._service(time_fired, cmd_name)

    async def service_automated(self, time_fired, cmd_name):
        await self._service(time_fired, cmd_name)

    #
    #
    #

    async def update(self, time_fired, state_update):
        # self.log(time_fired)

        # Get new state by applying state update to current state
        new_state = {**self.state, **state_update}

        # Perform actions on this area if state is changed
        if time_fired < self.last_update:
            self.log("Old update!")
        elif new_state != self.state:
            # Update state to new state
            self.last_update = time_fired
            self.state = new_state
            # self.log("Updated: {}".format(self.state))
            await self._update_area()

        # Propagate state update to all sub areas
        for sub_area in self.sub_areas:
            await self.create_task(sub_area.update(time_fired, state_update))

    #
    #
    #

    async def _service(self, time_fired, cmd_name):
        if cmd_name == "on":
            await self.update(time_fired, {
                "on": True
            })
        elif cmd_name == "off":
            await self.update(time_fired, {
                "on": False
            })
        elif cmd_name == "dim_up":
            await self.update(time_fired, {
                "on": True,
                "brightness_pct": min(100, self.state["brightness_pct"] + 5)
            })
        elif cmd_name == "dim_down":
            if self.state["on"]:
                await self.update(time_fired, {
                    "brightness_pct": max(1, self.state["brightness_pct"] - 5)
                })

    async def _update_area(self):
        if not self.area_id:
            return

        if self.task_1 and not self.task_1.done():
            if not self.waiting:
                self.waiting = True
                self.log("Waiting")
                await asyncio.wait_for(self.task_1, None)
                self.waiting = False

        if self.state["on"]:
            self.task_1 = await self.create_task(
                self.call_service(
                    "light/turn_on",
                    area_id=self.area_id,
                    kelvin=self.state["kelvin"],
                    brightness_pct=self.state["brightness_pct"]
                )
            )
        else:
            self.task_1 = await self.create_task(
                self.call_service(
                    "light/turn_off",
                    area_id=self.area_id
                )
            )

    async def terminate(self):
        pass
