# googlemapsearch
Search Google places with Google places API in Python and visualize them in Bokeh.
E.g. search for thai restaurants in Copenhagen within a certain radius.
Plot the results including rating, pricelevel and reviews in Bokeh.

prerequisites:

Google API token:
You need your own Google API token. You will get $300 to spent on calling their api's.
After approx 25 calls you reached your limit and you wil get an "OVER_QUERY_LIMIT" message.
You can ignore that and run your script again or wait till the next day

Bokeh:
Install Bokeh through pip
I found an issue after a certain number of plots, I thought it was the google maps limitations, but found out that it is the Bokeh javascripts library that is not loading: "Bokeh: ERROR: Unable to run BokehJS code because BokehJS library is missing"

I did not find a workaround or solution for this error.
I tried with env variable in windows: "set BOKEH_RESOURCES=CDN" or "set BOKEH_RESOURCES=INLINE"
and tried with bokeh outputfile methos: "output_file("yourtitle.html", mode="inline")
Neither of them worked
