# Discord Scraper

## Table of Contents
* [Configuring Discord application for PC](#desktop-application)
* [Configuring Discord website for PC](#website)
* [Notes](#notes)
* [Changelog](#changelog)

## Configuring

### Desktop Application:

Step 1:
Open your Discord app and enter the app settings.
![vwJ4kp5.png](https://i.imgur.com/vwJ4kp5.png "Step 1")

Step 2:
Traverse to Appearance and enable Developer Mode if it is disabled.
![35zu4Wt.png](https://i.imgur.com/35zu4Wt.png "Step 2a")
![YEad6fw.png](https://i.imgur.com/YEad6fw.png "Step 2b")

### Website:

Step 3:
Close the app settings and press CTRL + SHIFT + I to open the Developer panel.

Step 4:
Go to the Network tab and select from any personal message or server in your list.
Copy the value of "authorization" into the config.json file.
![kzix1jI.png](https://i.imgur.com/kzix1jI.png "Step 4a")
![AeCWWkp.png](https://i.imgur.com/AeCWWkp.png "Step 4b")

Step 5:
Close the Developer panel and right-click on the server icon and copy ID.
Paste the server ID into the config.json file.
![32VP97z.png](https://i.imgur.com/32VP97z.png "Step 5a")
![9Ev2dxU.png](https://i.imgur.com/9Ev2dxU.png "Step 5b")

Step 6:
Right-click on the channel name and copy ID.
Paste the channel ID into the config.json file.
![okhdZtQ.png](https://i.imgur.com/okhdZtQ.png "Step 6a")
![ZcdqQfr.png](https://i.imgur.com/ZcdqQfr.png "Step 6b")

Step 7:
Run the script to start the downloading process.

## Notes

* You can copy in multiple channels on multiple servers if you want to.
* You must make modifications to the JSON file before running the script (otherwise you'll end up with errors).
