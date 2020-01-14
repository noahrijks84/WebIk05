# Project "Scrivia" door: IK05

## Scrivia 

Dit is een trivia website waarbij een persoon de trivia tekent en de andere 3 spelers moeten dan raden wat het antwoord is op basis van de tekening en hun kennis. Het is een combinatie van pictionary en trivia spellen. Je kan met je vrienden een lobby maken waarin je een spel kan beginnen. Tussentijds kan je ook chatten. Voordat een spel begint kan je categorieën kiezen en de moeilijkheidsgraag instellen. Op basis van de snelheid waarbij je antwoord krijg je punten en de tekenaar krijgt punten voor iedereen die zijn tekening goed raadt, dit natuurlijk om de tekenaar te stimuleren duidelijke tekeningen te maken. Er is ook een leaderboard en een simpel ranking systeem waarbij je punten krijgt voor je performance en punten aftrek krijgt voor verlies. Gebruikers hebben ook een klein persoonlijk profiel waar ze hun ranking kunnen zien en een profile picture kunnen instellen. 

### Features 

1. Gebruikers moeten mensen kunnen uitnodigen via een link
2. Er moet een gebruiker worden gekozen die mag tekenen en die (als enige) het antwoord op de trivia vraag te zien krijgt
3. Gebruikers kunnen een nieuwe match starten met een andere gebruiker (tot een maximum van 4 gebruikers)
4. Gebruikers moeten een profiel aan kunnen maken (met een profiel foto) en waar ze hun ranking en leaderboard positie te zien kunnen krijgen

### Afhankelijkheden  

1. Databronnen: jService.io
2. Externe componenten: Boostrap voor website design, Adobe XD voor concept
3. Concurrerentie: Sporcle, Queendom
4. Moeilijkste delen: teken-aspect, lobbies, ranking systeem

### Minimum viable product

1. Er moet een gebruiker worden gekozen die mag tekenen en die (als enige) het antwoord op de trivia vraag te zien krijgt
2. Het creëren van lobby's met een maximum aantal van 4 personen
3. Gebruikers kunnen trivia vragen beantwoorden en daarmee punten scoren

## Technisch ontwerp

### Flowchart
![Flowchart](https://i.ibb.co/FnffKBb/Wireframe-Flowchart.png)

### Controller

/landingpage
* Dit is de homepage. Dit is de landingpage voor de gebruiker. Hier wordt het spel uitgelegd en de gebruiker kan hier naar de inlogpagina en de registratiepagina verwezen worden
* Dit is een GET request

![landingpage](https://i.ibb.co/R0p3SFB/Home-page-1.png)

/homepage
* Dit is de homepage als de gebruiker ingelogd is. De gebruiker kan vanaf hier naar veschillende pagina's navigeren zoals de profielpagina, leaderboard en gamemode. Er verschijnt ook een "burger" dropdown menu
* Dit is een POST request

![homepage](https://i.ibb.co/YkWfVdb/Home-page-logged-in.png)
* Dit is hoe het navigatie menu er uit ziet als het aangeklikt is.

![navigation](https://i.ibb.co/t4HSqB4/Nav-system.png)

/leaderboard
* Op deze pagina kan de gebruiker de leadersboard vinden. Dit is een overzicht van de statistieken van alle spelers onderverdeeld in categorieën
* Dit is een GET request.

![leaderboards](https://i.ibb.co/GxgF5z8/Leaderboard-Page.png)

/game
* Dit is de gamepagina, hier speelt het spel zich af. Er is hier ruimte voor een chatfunctie. Hier komt ook het canvas waarop getekend wordt en waar de spelers kunnen raden wat er getekend is
* Dit is een POST request

![game](https://i.ibb.co/DzqmkxQ/Game-page-1.png)

/profile
* De gebruiker kan hier zijn profiel bekijken. Hier komt de profielinformatie en kan dat ook aangepast worden (wachtwoord veranderen). De statistieken van de speler kunnen hier ook terug gevonden worden
* Dit is een POST request

![profilepage](https://i.ibb.co/n6wsVtt/Profile-Page.png)
* Dit is het password change scherm

![changepassword](https://i.ibb.co/1qPMpjK/Change-Password.png)

/lobbypage
* Hier kan de gebruiker lobbies aanmaken en joinen
* Dit is een POST request

![lobbypage](https://i.ibb.co/Rpq88hB/Game-page-1.png)

/login
* Dit is de inlogpagina
* Dit is een POST request

![login](https://i.ibb.co/syqVdQp/Login-page.png)

/register
* Dit is de registratiepagina
* Dit is een POST request

![registration](https://i.ibb.co/FswX08c/Register-Page-1.png)

### Models/helpers

1. Log out helper functie. Deze nemen we over van finance om gebruikers uit te loggen.

### Plugins/frameworks

1. Flask. Documentatie: http://flask.palletsprojects.com/en/1.1.x/
2. Bootstrap. Documentatie:
https://getbootstrap.com/docs/4.1/getting-started/introduction/
3. jQuery Drawing Plugin. Documentatie: https://www.jqueryscript.net/other/Drawing-Signature-App-jQuery-Canvas.html
4. Socket. Documentatie: 
https://socket.io/docs/






















