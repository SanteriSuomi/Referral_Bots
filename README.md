# ReferralBots

Bot(s) for automatising referrals for contests on platforms such as SweepWidget. Originally created to easily get referral points for cryptocurrency whitelist contests. 
At the moment of writing this, able to handle most types of SweepWidget "anti-bot" methods such as email verification and captcha (with Anti-Captcha extension). Does sometimes get caught in anti-spam filter, but this is likely unavoidable. The bot keeps trying until it completes the amount of referrals you want to give to the specified user.

SweepWidget bot (SW_bot.py)
  Prerequisites:
  - GeckoDriver (free)
  - Private Internet Access (paid service)
  - Anti-captcha extension (paid service)
  - Random user-agent extension (free)
  - Bunch of Python libraries installed (free)
  Recommendations:
  Use with a virtual machine such as VMware Workstation of VirtualBox. Personally tested on VirtualBox. This way, the bot does not interfere your main desktop and you can also run   multiple instances of the bot by cloning your virtual machine. Running multiple instances does require a decent amount of RAM and CPU cores though (I have 32GB of RAM and i7-     8700k, and can run 5 VMs effortlessly, while still being able to do stuff on my main desktop).
