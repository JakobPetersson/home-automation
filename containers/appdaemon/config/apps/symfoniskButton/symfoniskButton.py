import hassapi as hass

import time

class SymfoniskButton(hass.Hass):

	def initialize(self):
		self.init_button()
		self.init_debounce()
		self.init_volume()


	def init_button(self):
		button_ieee = self.args.get("button_ieee")
		self.event_listen_handle = self.listen_event(
			self.event_cb,
			"zha_event",
			device_ieee = button_ieee
		)


	def init_debounce(self):
		self.last_command = None
		self.last_command_ms = 0
		self.debounce_interval_ms = 500


	def init_volume(self):
		self.volume_interval_s = 0.2
		self.volume_timer_handle = None


	def event_cb(self, event_name, data, kwargs):
		command = data["command"]
		args = data["args"]

		if command == "toggle":
			self.debounce_command("media_player/media_play_pause")
		elif command == "step":
			if args == [0, 1, 0]:
				self.debounce_command("media_player/media_next_track")
			elif args == [1, 1, 0]:
				self.debounce_command("media_player/media_previous_track")
		elif command == "move":
			if args == [0, 195]:
				self.debounce_command("media_player/volume_up")
			elif args == [1, 195]:
				self.debounce_command("media_player/volume_down")
		elif command == "stop":
			self.debounce_command(None)


	def debounce_command(self, command):
		now_ms = int(round(time.time() * 1000))
		if command == self.last_command and (now_ms - self.last_command_ms) <= self.debounce_interval_ms:
			return
		self.last_command = command
		self.last_command_ms = now_ms

		self.cancel_volume_timer()

		if not command:
			return
		elif command == "media_player/volume_up" or command == "media_player/volume_down":
			self.start_volume_timer(command)
		else:
			self.send_command({"command": command})


	def send_command(self, kwargs):
		command = kwargs["command"]
		#self.log(command)
		self.call_service(
			command,
			entity_id = self.args.get("media_player")
		)


	def start_volume_timer(self, command):
		self.volume_timer_handle = self.run_every(
			self.send_command,
			"now",
			self.volume_interval_s,
			command = command
		)


	def cancel_volume_timer(self):
		if self.volume_timer_handle != None:
			self.cancel_timer(self.volume_timer_handle)
			self.volume_timer_handle = None


	def terminate(self):
		self.cancel_listen_event(self.event_listen_handle)
