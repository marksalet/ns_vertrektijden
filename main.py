# Import the modules that will be used in this python file.
app = Flask(__name__)

# This sets the authentication details for the NS API to use.
auth_details = ('marksalet@gmail.com', 'O3-zrii9Xa27xh73xQ1WUD8cSw2p7C0_fM-4Y39USVwvsd3KoDdumQ')

# Defines what should happen if you land on the root.
# Here we will show a list with all the available stations.
@app.route("/")
def home():

    api_url_stations = 'http://webservices.ns.nl/ns-api-stations-v2'
    responseStations = requests.get(api_url_stations, auth=auth_details)

    stationsXML = xmltodict.parse(responseStations.text)

    stationList = "<ul>"

    for station in stationsXML['Stations']['Station']:
        if station['Land'] == 'NL':

            stationName = station['Namen']['Lang'].replace("a/d", "aan den")
            stationCode = station['Code']

            stationList += '<li><a href="/vertrektijden/%s/%s">&#x27A4; %s</a></li>' % (stationCode, stationName, stationName)

    stationList += "</ul>"
    stationListCode = Markup(stationList)

    return render_template('layout.html', stationList=stationListCode)

# Defines what should happen if you land on the URL /vertrektijden/stationcode.
# Here we will show all the department times form the station.
@app.route("/vertrektijden/<string:thisstation>/<string:stationname>")
def vertrektijden(thisstation, stationname):

    # this_station_code sets the code from the station where the application is running.
    # This has to be set by hand to show the first time. Later can be chosen by the user to show there wanted station.
    this_station_code = thisstation
    stationname = stationname

    api_url_vertrek = 'http://webservices.ns.nl/ns-api-avt?station=' + this_station_code
    responseVertrek = requests.get(api_url_vertrek, auth=auth_details)

    vertrekXML = xmltodict.parse(responseVertrek.text)
    table = '<table><tr class="tableHeader"><th>Tijd</th><th>Naar</th><th>Vervoerder</th><th>Spoor</th></tr>'
    if 'ActueleVertrekTijden' in vertrekXML:
        for vertrek in vertrekXML['ActueleVertrekTijden']['VertrekkendeTrein']:
            eindbestemming = vertrek['EindBestemming']
            if 'RouteTekst' in vertrek:
                vertrekvia = vertrek['RouteTekst']
            vertrektijd = vertrek['VertrekTijd']      # 2016-09-27T18:36:00+0200
            vertrektijd = vertrektijd[11:16]          # 18:36
            if '#text' in vertrek['VertrekSpoor']:
                vertrekspoor = vertrek['VertrekSpoor']['#text']
            else:
                vertrekspoor = '1'
            vertrekvervoerder = vertrek['Vervoerder']
            table += '<tr valign="top" class="trMain"><td> %s </td><td> %s ' % (vertrektijd, eindbestemming)
            if 'RouteTekst' in vertrek:
                table += '</br><span class="via">Via: %s</span>'    % (vertrekvia)
            table += '</td><td> %s </td><td> %s </td></tr>' % (vertrekvervoerder, vertrekspoor)
    else:
        table += '<tr><td><b>Er zijn geen vertrektijden van dit station.</b></td></tr>'

    table += '</table>'
    tableCode = Markup(table)

    return render_template('vertrektijden.html', vertrektijden=tableCode, stationname=stationname)


if __name__ == "__main__":
    app.run()
