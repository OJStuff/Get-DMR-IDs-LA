# Introduksjon

Dette programmet er beregnet for radioamatørbruk, spesielt for norske radioamatører. Det er basert på programmet "Get-DMR-IDs", men har en utvidelse som gjør at det kan laste ned og bruke data fra NKOM for å opdatere DMR IDer fra radioid.net. Det kjører fra kommandolinjen, og oppretter og eksporterer et utvalg DMR-IDer til en fil i csv-format, som kan importeres til AnyTone D878/D578 DMR-radioer. Du må imidlertid bruke programvaren levert av radioprodusenten for å importere filen til radioen. Programmet kan også eksportere til en vanlig tekstfil (men dette er ikke ment for noen radio).

## Programmet

Nedlastede data fra [radioid.net](https://radioid.net) (users.json) kommer i json dataformat. Programmet henter landskoder fra filen [country_codes.py](country_codes.py) og regionkoder fra filen [region_codes.py](region_codes.py) for å identifisere valgte regioner og land for eksport. Nedlastede data fra [NKOM](https://nkom.no) (Liste over norske radioamatører (CSV).csv) er i csv-format, og brukes for å komplettere data fra radioid.net.

Hvis du vil se en liste over alle tilgjengelige regionkoder, kan du prøve denne skallkommandoen på programmets plassering:

    more region_codes.py

Hvis du vil se en liste over alle tilgjengelige landskoder, kan du prøve denne skallkommandoen på programmets plassering:

    more country_codes.py

Alle data fra radioid.net (users.json) er i UTF-8-format, som ikke er veldig radioenhetsvennlig. Alle data som eksporteres fra programmet vil derfor bli oversatt til ASCII-format med unidecode-biblioteket. Dette biblioteket må derfor være installert før du kan kjøre programmet. Installasjonen av dette biblioteket kan gjøres med denne skallkommandoen:

    pip install unidecode

## Komme i gang

### Eksempel 1

Denne kommandoen viser hvordan du får hjelp til å bruke programmet:

    >python getdmridsla.py -h

    usage: getdmridsla.py [-h] [-s] [-d] [-dla] [-f {anytone,text}]
                      [-r [REGION ...]] [-c [COUNTRY ...]]

    Program exports a formatted file with DMR IDs based on users criteria. This
    file can be imported into a radio, like AnyTone D878/D578, as digital contact
    list

    options:
    -h, --help            show this help message and exit
    -s, --statistics      show statistics for formatted file with dmr-id's
    -d, --download        download DMR database from https://radioid.net
    -dla, --downloadLA    download LA database from https://nkom.no
    -f {anytone,text}, --format {anytone,text}
                            file format for the formatted file
    -r [REGION ...], --region [REGION ...]
                            region codes added for the formatted file
    -c [COUNTRY ...], --country [COUNTRY ...]
                            country codes added/subtracted for the formatted file

    Updated version and resources may be found at https://GitHub.com/OJStuff

### Eksempel 2

Denne kommandoen spesifiserer å laste ned en oppdatert rå DMR ID-brukerdatabase og norsk brukerdatabase fra NKOM, og deretter opprette formatert eksportfil for region 2 (Europa). Filformatet vil være for standard filformat (AnyTone D878/D578) og filen vil få navnet "users-anytone.csv":

    >python getdmridsla.py -d -dla -r 2

    Downloading DMR database "users.json" > 41.71 MB downloaded
    Downloading LA database "Liste over norske radioamatører (CSV).csv" > 0.58 MB downloaded
    Options specified for export of formatted file:
    -r 2 include region: Europe
    Getting DMR IDs from "users.json"
    Updating IDs from "Liste over norske radioamatører (CSV).csv"
    DMR ID file "users-anytone.csv" was exported with 95,334 IDs

### Eksempel 3

Denne kommandoen spesifiserer å opprette formatert eksportfil for region 2 (Europa). Land 302 (Canada) vil også bli lagt til samlingen, men Norge (242) vil bli ekskludert. Filformatet vil være for standard filformat (AnyTone D878/D578) og filen vil få navnet "users-anytone.csv":

    >python getdmridsla.py -r 2 -c 302 -242

    Options specified for export of formatted file:
    -r 2 include region: Europe
    -c 302 include country: Canada
    -c -242 exclude country: Norway
    Getting DMR IDs from "users.json"
    Updating IDs from "Liste over norske radioamatører (CSV).csv"
    DMR ID file "users-anytone.csv" was exported with 100,320 IDs

### Eksempel 4

Denne kommandoen spesifiserer å lage formatert eksportfil for region 1, 2 og 3 med statistikk. Filformatet vil være for standard filformat (AnyTone D878/D578) og filen vil få navnet "users-anytone.csv":

    >python getdmridsla.py -r 1 2 3 -s

    Options specified for export of formatted file:
    -r 1 include region: North America and Canada
    -r 2 include region: Europe
    -r 3 include region: North America and the Caribbean
    Getting DMR IDs from "users.json"
    Updating IDs from "Liste over norske radioamatører (CSV).csv"
    DMR ID file "users-anytone.csv" was exported with 219,702 IDs

    Statistics for exported formatted file:
            0 IDs from region 0: Test networks
        8,861 IDs from region 1: North America and Canada
    95,334 IDs from region 2: Europe
    115,507 IDs from region 3: North America and the Caribbean
            0 IDs from region 4: Asia and the Middle East
            0 IDs from region 5: Australia and Oceania
            0 IDs from region 6: Africa
            0 IDs from region 7: South and Central America
            0 IDs from region 8: Not used
            0 IDs from region 9: Worldwide (Satellite, Aircraft, Maritime, Antarctica)
