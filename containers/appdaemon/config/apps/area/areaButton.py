import hassapi as hass

import datetime

class AreaButton(hass.Hass):

	async def initialize(self):
		await self.init_button()
		await self.init_dimmer()
		await self.init_area()
		self.dim_interval_s = 0.2


	async def init_button(self):
		button_ieee = self.args.get("button_ieee")
		self.event_listen_handle = await self.listen_event(
			self.event_cb,
			"zha_event",
			device_ieee = button_ieee
		)


	async def init_dimmer(self):
		self.dimmer_timer_handle = None


	async def init_area(self):
		self.room = None
		area_name = self.args.get("area_name")
		if area_name:
			self.room = await self.get_app(area_name)
			self.log("Room: {}".format(self.room))
		else:
			pass
			#self.log("No room")


	async def event_cb(self, event_name, data, kwargs):
		command = data["command"]
		time_fired = datetime.datetime.fromisoformat(data["metadata"]["time_fired"])

		await self.cancel_dimmer_timer()
		if command == "on":
			#self.log("Click on")
			await self.room.service_manual(time_fired, "on")
		elif command == "off":
			#self.log("Click off")
			await self.room.service_manual(time_fired, "off")
		elif command == "move_with_on_off":
			self.dimmer_timer_handle = await self.run_every(
				self.dim_up,
	            "now",
	            self.dim_interval_s
	        )
		elif command == "move":
			self.dimmer_timer_handle = await self.run_every(
				self.dim_down,
	            "now",
	            self.dim_interval_s
	        )
		elif command == "stop":
			pass
			#self.log("Let go")


	async def cancel_dimmer_timer(self):
		if self.dimmer_timer_handle != None:
			await self.cancel_timer(self.dimmer_timer_handle)
			self.dimmer_timer_handle = None


	async def dim_up(self, kwargs):
		#self.log("Dim up")
		if self.room:
			time_fired = datetime.datetime.utcnow()
			await self.room.service_manual(time_fired, "dim_up")


	async def dim_down(self, kwargs):
		#self.log("Dim down")
		if self.room:
			time_fired = datetime.datetime.utcnow()
			await self.room.service_manual(time_fired, "dim_down")


	async def terminate(self):
		await self.cancel_listen_event(self.event_listen_handle)
