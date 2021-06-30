import hassapi as hass
import copy

import asyncio

class Area(hass.Hass):

    async def initialize(self):

        self.area_id = self.args.get("area_id")

        self.task_1 = None
        self.waiting = False

        await self.init_sub_areas()

        self.state = {}
        await self._update(None, {
            "on": False,
            "kelvin": 3500,
            "brightness_pct": 100
        })


    async def init_sub_areas(self):
        sub_areas_name = self.args.get("sub_areas") or []
        self.sub_areas = []
        for area_name in sub_areas_name:
            sub_area = await self.get_app(area_name)
            self.log(sub_area)
            self.sub_areas.append(sub_area)


    #
    # Services (Called from  other apps)
    #

    async def service_manual(self, time_fired, cmd_name):
        if cmd_name == "on":
            await self._update(time_fired, {
                "on": True
            })
        elif cmd_name == "off":
            await self._update(time_fired, {
                "on": False
            })
        elif cmd_name == "dim_up":
            await self._update(time_fired, {
                "on": True,
                "brightness_pct": min(100, self.state["brightness_pct"] + 5)
            })
        elif cmd_name == "dim_down":
            if self.state["on"]:
                await self._update(time_fired, {
                    "brightness_pct": max(1, self.state["brightness_pct"] - 5)
                })


    async def service_turn_on_manual(self, time_fired):
        await self.service_manual(time_fired, "on")


    async def service_turn_off_manual(self, time_fired):
        await self.service_manual(time_fired, "off")


    async def service_dim_up_manual(self, time_fired):
        await self.service_manual(time_fired, "dim_up")


    async def service_dim_down_manual(self, time_fired):
        await self.service_manual(time_fired, "dim_down")

    #
    #
    #


    async def _update(self, time_fired, state_update):
        self.log(time_fired)
        new_state = {**self.state, **state_update}

        if new_state != self.state:
            self.state = new_state
            self.log("Updated: {}".format(self.state))
            await self._update_area(time_fired)

        await self._update_sub_areas(time_fired, state_update)


    async def _update_sub_areas(self, time_fired, state_update):
        for sub_area in self.sub_areas:
            await self.create_task(sub_area._update(time_fired, state_update))


    #
    # Update
    #
    async def _update_area(self, time_fired):
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
                    area_id = self.area_id,
                    kelvin = self.state["kelvin"],
                    brightness_pct = self.state["brightness_pct"]
                )
            )
        else:
            self.task_1 = await self.create_task(
                self.call_service(
                    "light/turn_off",
                    area_id = self.area_id
                )
            )


    async def terminate(self):
        pass
