import hassapi as hass


class AreaDevice(hass.Hass):

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

    async def terminate(self):
        await self.cancel_listen_event(self.event_listen_handle)
