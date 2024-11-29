# A list of things I didn't do correctly but should fix soon.

- **[ ]** **PIXI Aquarium click events** - In the front end, the main PIXI `app` is what listens for the click. This should be bound to the Aquarium class instead!
    - kind of fixed... it's bound to the background sprite now. But it's still not ideal.

- **[ ]** **Fix GuestUser login** I've added a function decorated with `@login_manager.request_loader` in intergrated with sessions to try log in guest users `__init__.py`. But it's not really working. Whenever I refresh, I get assigned a different guest user. Also each SocketIO event has a different `current_user`. It's not ideal.

- **[✅]** **Documentation on interaction verification** - ~~Right now verification of interactions is done in the event handler (`/events/interactions.py`). This is probably okay, but we should write it down somewhere. The other option is to do it in `simulate.py`, but that feels bad. There's also the option of writing it into the `UserManager` class...~~ I added the function decorator `@confirm_user` to events that require user verification (like those in `interactions.py`). The function itself is declared in `helper.py` :) I'm proud of this solution!

- **[ ]** **Error feedback on selecting tools** - When a user tries to select a tool that they can't afford, there should be some feedback. Right now, nothing happens. When they try to use it the tool disappears which is good. But like it maybe should flash red or something when they try to select it in the first place.

- **[✅]** **FIX FISH INTERPOLATION CLIENTSIDE** - ~~Right now, we're assume the client and server computers are synced to the same epoch time to do the interpolation. We just calculate the time difference between the server and client and use that to calculate the fish position. This is bad! We should just move the fish toward its destination regardless of the server time!~~ I fixed this by logging local time when a server update comes in and using that to interpolate the fish position. It works surprisingly smoothly even when deployed on the internet!

- **[ ]** **Clean up save to S3 methods** - I'm unable to retrieve all objects from a directory in the DO Spaces S3 bucket, but I'm still able to save and load given a specific endpoint. My workaround is that in  `aquarium.save()` I'm calling `save_to_s3()` where the filename is our datetime convention but I'm also saving extra file called `latest.pkl` which is the same. Ideally this gets overwritten every time each time I save, and `load_latest_from_s3()` will just load the `latest.pkl` file rather than searching through the directory for the latest file. It works for now, but it's not ideal. We're also doing this with `store.save()`

- **[ ]** **Fix frontend cursor animations** - The cursor animations work fine, but the way we handle the textures and animations use a lot of hardcoded names, so that's annoying... There are also a few workarounds for resetting the texture, etc. Check out the `Cursor` class in `interactionModels.js` for more info.

- **[ ]** **Fix deployment with Gunicorn and eventlet** - Check `deployment.md` for more info. It's annoying.

- **[✅]** **Actually calculate health and hunger** - ~~I have to do some math to set reasonable values...~~ I have some equations modeling this for now... We'll see how well it works. We should also eventually entangle this with the fish happiness system.

- **[ ]** **Implement fish happiness** - This is a big one. The fish should do different things based on its happiness. Use this for health and coin drops too! It should prefer some users more, and react to things like being fed and glass taps differently. I have to really think about how to implement this.

- **[ ]** **Make different foods have different nutritional values for each fish** - I should roll this into the `Fish.food_preferences` attribute and somehow incorporate that into the `_eat()` method. I'll have to write code to match a Thing's class hierarchy to a string :) ALSO MAKE THIS AFFECT GROWTH RATE SOMEHOW! RIGHT NOW IT'S JUST AN UNSOPHISTICATED ADDITION TO WIDTH!

- **[ ]** **Credit the creators of stuff** - I found `first-names.txt` from [this repo](https://github.com/dominictarr/random-name/tree/master). Most of my game assets are from [Olga's Lab](https://olgas-lab.itch.io/2d-huge-underwater-themed-bundle) and the cursors are from [DreamXP](https://dreamxpstudio.itch.io/handy-handz-cursor-pack), though I paid for both of those :)
