import requests
import configparser
import flask
from flask import Flask, render_template, request
from flask_datadog import API, StatsD, initialize
from datadog import initialize, api
from datetime import datetime
app = Flask(__name__)

options = {
    'api_key': '<REDACTED>',
    'app_key': '<REDACTED>'
}
initialize(**options)


class event_builder:
    title1 = "Temperature discrepancy"
    text1 = "The temperature difference between actual and feels like is greater than 5 degrees."
    tags1 = ['application:web', 'tag:discrepancy']
    title2 = "Temperature is near freezing."
    text2 = "The temperature is close to freezing. Freeze Advisory."
    tags2 = ['application:web', 'tag:freezewarning']
    title3 = "Temperature is at heat advisory levels."
    text3 = "The temperature difference is very hot. Heat Advisory."
    tags3 = ['application:web', 'tag:heatwarning']
    title4 = "It is currently raining in the selected city."
    text4 = "It is currently raining. "
    tags4 = ['application:web', 'tag:rainwarning']
    title5 = "It is currently snowing in the selected city."
    text5 = "It is currently snowing."
    tags5 = ['application:web', 'tag:snowwarning']


eb = event_builder()
# https://github.com/DataDog/datadogpy


@app.route('/',methods=['GET','POST'])
def weather_dashboard():
    zip_code="94102"
    if flask.request.method == 'POST':
        if request.form['zipCode'] is None:
                zip_code="94102"
        else:
    		zip_code = request.form['zipCode']
    api_key = get_api_key()
    data = get_weather_results(zip_code, api_key)
    temp = "{0:.2f}".format(data["main"]["temp"])
    feels_like = "{0:.2f}".format(data["main"]["feels_like"])
    weather = data["weather"][0]["main"]
    location = data["name"]
    event_trigger(zip_code)
    # print(type(temp))
    return render_template('results.html',
                           location=location, temp=temp,
                           feels_like=feels_like, weather=weather)


def event_trigger(zip_code):
    api_key = get_api_key()
    data = get_weather_results(zip_code, api_key)
    temp = "{0:.2f}".format(data["main"]["temp"])
    feels_like = "{0:.2f}".format(data["main"]["feels_like"])
    weather = data["weather"][0]["main"]
    location = data["name"]
    temp_check = float(temp)
    feel_check = float(feels_like)
    weather_check = str(weather)
    temp_diff = temp_check - feel_check
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    location = " City: %s. Temperature is: %dF" % (location, temp_check)
    location1 = " Feels like: %sF" % (feel_check)
    location = location+location1
    timeoutput = " @ %s" % (current_time)
    details = location+timeoutput
    print(location)
    print(timeoutput)
    if temp_diff > 6:
        print("temp_diff greater than 5 degrees")
        text1 = eb.text1+details
        api.Event.create(title=eb.title1, text=text1, tags=eb.tags1)
    if temp_check < 40:
        print("Freeze warning")
        text2 = eb.text2+details
        api.Event.create(title=eb.title2, text=text2, tags=eb.tags2)
    if temp_check > 80:
        print("Heat warning")
        text3 = eb.text3+details
        api.Event.create(title=eb.title3, text=text3, tags=eb.tags3)
    if weather_check == "Rain":
        print("Raining")
        text4 = eb.text4+details
        api.Event.create(title=eb.title4, text=text4, tags=eb.tags4)
    if weather_check == "Snow":
        print("Snowing")
        text4 = eb.text4+details
        api.Event.create(title=eb.title5, text=text5, tags=eb.tags5)


def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['openweathermap']['api']


def get_weather_results(zip_code, api_key):
    api_url = "http://api.openweathermap.org/" \
              "data/2.5/weather?zip={}&units=imperial&appid={}".format(
                  zip_code, api_key)
    r = requests.get(api_url)
    return r.json()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=False)
