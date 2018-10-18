# TwitchAnalytics
Collecting and analyzing Twitch.tv viewer data and video game stock performance.

TwitchDataScript.py is what's running on a cloud server to collect Twitch.tv and Yahoo Finance stock data.
All time is in UTC due to the server's local time.

The notebooks are preliminary analysis done as I collect more data.


Oct 10th

Let's look at the October 9th, 2018 Twitch data only for now. October_9th_Views.jpg shows the raw viewers over time on a five-minute interval.

Fortnite has the most views at any given time besides a brief period at 14h. It also has the largest dip in views, possibly due to its young viewers going to sleep.

There are significant dips in views at around 21.5h for PUBG and 23h for WOW. I was not watching either at the time, so this might be regular phenomena, or special events just ended. It’s interesting how the increase in views of PUBG between 8h to 17h looks concave down rather than up for the other games.

The total views seem to bottom out at around 8h (or 4am EDT), and peaked around the evening. 

The normalized views graph in October_9th_Normalized.jpg highlights other aspects. It’s the current views divided by the view count at 0h, which effectively normalizes it.

Fortnite’s large dip doesn’t look too bad if we normalize the data, compared to the first graph.

PUBG tripled its views between 8h and 20h. This is by far the most significant relative increase in that day so far. The fact that the relative views immediately dropped at 21.5h to that of other game streams suggests a special event that drew viewers occurred.

Most games seem to lose roughly half of its views. LOL seems to have the least amount of cyclicality for that day. Perhaps this is due to the international appeal of this game, with it especially popular in Asia.


Oct 18th

Still collecting data. Looking up Seasonal ARIMA models to see if they can be applied here.
