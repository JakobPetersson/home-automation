import areaDevice
import datetime


class AreaDoorSensor(areaDevice.AreaDevice):

    async def initialize(self):
        await super().initialize()
        self.log("AreaDoorSensor")

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
        await super().terminate()
