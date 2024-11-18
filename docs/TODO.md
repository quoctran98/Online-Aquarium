# A list of things I didn't do correctly but should fix soon.

- **[ ]** **PIXI Aquarium click events** - In the front end, the main PIXI `app` is what listens for the click. This should be bound to the Aquarium class instead!
    - kind of fixed... it's bound to the background sprite now. But it's still not ideal.

- **[ ]** **Fix GuestUser login** I've added a function decorated with `@login_manager.request_loader` in intergrated with sessions to try log in guest users `__init__.py`. But it's not really working. Whenever I refresh, I get assigned a different guest user. Also each SocketIO event has a different `current_user`. It's not ideal.

- **[ ]** **Documentation on interaction verification** - Right now verification of interactions is done in the event handler (`/events/interactions.py`). This is probably okay, but we should write it down somewhere. The other option is to do it in `simulate.py`, but that feels bad. There's also the option of writing it into the `UserManager` class...

- **[ ]** **Error feedback on selecting tools** - When a user tries to select a tool that they can't afford, there should be some feedback. Right now, nothing happens. When they try to use it the tool disappears which is good. But like it maybe should flash red or something when they try to select it in the first place.

- **[ ]** **FIX FISH INTERPOLATION CLIENTSIDE** - Right now, we're assume the client and server computers are synced to the same epoch time to do the interpolation. We just calculate the time difference between the server and client and use that to calculate the fish position. This is bad! We should just move the fish toward its destination regardless of the server time!