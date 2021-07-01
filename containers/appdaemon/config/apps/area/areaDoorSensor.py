import hassapi as hass
import datetime


class AreaDoorSensor(hass.Hass):

    async def initialize(self):
        await self.init_area()
        await self.init_device()

    async def init_area(self):
        self.area = None
        area_name = self.args.get("area_name")
        if area_name:
            self.area = await self.get_app(area_name)
            if not self.area:
                self.log("Area not initialized, {}".format(area_name))
        else:
            pass

    async def init_device(self):
        device_ieee = self.args.get("device_ieee")
        self.event_listen_handle = await self.listen_event(
            self.event_cb,
            "zha_event",
            device_ieee=device_ieee
        )

    async def event_cb(self, event_name, data, kwargs):
        command = data["command"]
        args = data["args"]
        time_fired = datetime.datetime.fromisoformat(data["metadata"]["time_fired"])

        if command == "attribute_updated" and args["attribute_name"] == "on_off":
            if args["value"] == 1:
                await self.area.service_automated(time_fired, "on")
            if args["value"] == 0:
                await self.area.service_automated(time_fired, "off")

    async def terminate(self):
        await self.cancel_listen_event(self.event_listen_handle)
