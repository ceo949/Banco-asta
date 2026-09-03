#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BANCO D'ASTA v2.0 — assistente per l'asta del fantacalcio
Serie A 2026/27 · listone ufficiale Fantacalcio.it · pensato per iPad

Solo libreria standard di Python. Avvia lo script e apri http://127.0.0.1:8788
Lo stato dell'asta si salva in asta_stato_v2.json accanto allo script.
"""

import json, os, re, sys, threading, webbrowser, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "2.2"
PORT = 8788
HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, "asta_stato_v2.json")

# ============================================================
#  LISTONE UFFICIALE Fantacalcio.it — stagione 2026/27
#  R | Nome | Squadra | Quotazione | FVM | titolarita' (3/2/1)
# ============================================================
RAW = """P|Svilar|Roma|19|85|3
P|Vicario|Juventus|17|70|3
P|Martinez Jo.|Inter|17|68|3
P|Carnesecchi|Atalanta|17|55|3
P|Maignan|Milan|15|52|3
P|Butez|Como|15|50|3
P|Meret|Napoli|11|48|3
P|Mandas|Lazio|10|36|3
P|Skorupski|Bologna|10|32|3
P|De Gea|Fiorentina|11|30|3
P|Okoye|Udinese|9|28|3
P|Falcone|Lecce|8|26|3
P|Perri|Torino|9|26|3
P|Caprile|Cagliari|10|25|3
P|Sanchez Ro.|Como|8|25|2
P|Bijlow|Genoa|8|15|3
P|Muric|Sassuolo|7|15|3
P|Palmisani|Frosinone|5|12|3
P|Stankovic F.|Venezia|6|11|3
P|Tornqvist|Monza|1|10|3
P|Corvi|Parma|2|10|3
P|Daffara|Parma|6|7|2
P|Provedel|Inter|2|5|2
P|Thiam|Monza|4|5|2
P|Milinkovic-Savic V.|Napoli|5|5|2
P|Mascardi|Torino|1|5|2
P|Sportiello|Atalanta|1|1|2
P|Pompei|Atalanta|1|1|1
P|Happonen|Bologna|1|1|2
P|Pessina Mas.|Bologna|1|1|1
P|Sherri|Cagliari|1|1|2
P|Radunovic|Cagliari|1|1|1
P|Vigorito|Como|1|1|1
P|Christensen O.|Fiorentina|1|1|2
P|Lezzerini|Fiorentina|1|1|1
P|Desplanches|Frosinone|2|1|2
P|Lolic|Frosinone|1|1|1
P|Pisseri|Frosinone|1|1|1
P|Sommariva|Genoa|1|1|2
P|Stolz|Genoa|1|1|1
P|Di Gennaro|Inter|1|1|1
P|Pinsoglio|Juventus|1|1|2
P|Grabara|Juventus|1|1|1
P|Motta|Lazio|1|1|2
P|Renzetti|Lazio|1|1|1
P|Penev|Lecce|1|1|2
P|Bleve|Lecce|1|1|1
P|Terracciano|Milan|1|1|2
P|Torriani|Milan|1|1|1
P|Strajnar|Monza|1|1|1
P|Contini|Napoli|1|1|1
P|Ghidotti|Parma|1|1|1
P|De Marzi|Roma|1|1|2
P|Gollini|Roma|1|1|1
P|Russo A.|Sassuolo|1|1|2
P|Turati|Sassuolo|1|1|1
P|Satalino|Sassuolo|1|1|1
P|Paleari|Torino|1|1|1
P|Siviero|Torino|1|1|1
P|Padelli|Udinese|1|1|2
P|Piana|Udinese|1|1|1
P|Mrozek|Udinese|1|1|1
P|Grandi|Venezia|1|1|2
P|Pozzi|Venezia|1|1|1
P|Montipo|Venezia|1|1|1
D|Dimarco|Inter|31|240|3
D|Wesley|Roma|18|87|3
D|Molina N.|Roma|18|78|3
D|Bremer|Juventus|16|60|3
D|Rrahmani|Napoli|15|51|3
D|Mancini|Roma|16|50|3
D|Pavlovic|Milan|14|49|3
D|Akanji|Inter|15|47|3
D|Kalulu|Juventus|14|47|3
D|Solet|Udinese|13|46|3
D|Bastoni|Inter|14|43|3
D|N'Dicka|Roma|13|42|3
D|Ostigard|Genoa|11|41|3
D|Di Lorenzo|Napoli|12|39|3
D|Spence|Inter|11|37|3
D|Bisseck|Inter|12|36|2
D|Chalobah T.|Como|10|32|3
D|Ramon|Como|10|31|3
D|Gila|Milan|13|31|3
D|Vasquez|Genoa|9|30|3
D|Scalvini|Atalanta|10|28|3
D|Diego Carlos|Parma|8|26|3
D|Hermoso|Roma|11|26|2
D|Couto|Como|8|25|3
D|Stones|Inter|12|25|2
D|Tavares N.|Lazio|7|25|3
D|Spinazzola|Napoli|8|25|3
D|Miranda J.|Bologna|8|23|3
D|Bartesaghi|Milan|8|22|3
D|Valeri|Parma|8|22|3
D|Valle|Como|6|21|3
D|Delprato|Parma|8|21|3
D|Kristensen T.|Atalanta|6|20|3
D|Theate|Bologna|8|20|3
D|Mina|Cagliari|7|20|3
D|Dodo|Fiorentina|9|20|3
D|Dragusin|Fiorentina|7|20|3
D|Carlos Augusto|Inter|6|20|2
D|Marusic|Lazio|6|20|3
D|Romagnoli|Lazio|6|20|3
D|Tiago Gabriel|Lecce|8|20|3
D|De Winter|Milan|5|20|3
D|Belghali|Torino|7|20|3
D|Zappacosta|Atalanta|8|19|3
D|Zortea|Bologna|7|19|3
D|Sutalo J.|Lazio|7|19|3
D|Idzes|Sassuolo|7|19|3
D|Vojvoda|Udinese|9|19|3
D|Bernasconi|Atalanta|6|18|3
D|Jimenez A.|Fiorentina|7|18|3
D|Cambiaso|Juventus|8|18|3
D|Badiashile|Napoli|7|18|3
D|Bellanova|Atalanta|6|17|2
D|Lucumi|Juventus|7|17|3
D|Valdepenas|Fiorentina|5|16|3
D|Celik|Juventus|8|16|2
D|Doekhi|Lazio|8|16|2
D|Heggem|Bologna|6|15|3
D|Obert|Cagliari|7|15|3
D|Sugawara|Cagliari|6|15|3
D|Bracaglia|Frosinone|7|15|3
D|Gabbia|Milan|7|15|2
D|Mangas|Monza|7|15|3
D|Buongiorno|Napoli|6|15|2
D|Koulierakis|Roma|8|15|2
D|Caleta-Car|Sassuolo|6|15|3
D|Rodriguez Ju.|Cagliari|4|14|3
D|Marcandalli|Genoa|6|14|3
D|Pavard|Inter|6|14|1
D|Pedraza|Lazio|6|14|2
D|Kouadio|Monza|3|14|3
D|Troilo|Parma|3|14|3
D|Rensch|Roma|4|14|2
D|Coco|Torino|7|14|3
D|Holm|Bologna|6|13|2
D|Ze Pedro|Cagliari|5|13|2
D|Kaiki|Como|6|13|2
D|Kempf|Como|5|13|2
D|Monterisi|Frosinone|6|13|3
D|Calvani|Frosinone|5|13|3
D|Provstgaard|Lazio|4|13|2
D|Estupinan|Milan|3|13|2
D|Olivera|Napoli|5|13|2
D|Obrador|Sassuolo|6|13|3
D|Comuzzo|Torino|8|13|3
D|Ismajli|Torino|7|13|3
D|Bella-Kotchap|Venezia|5|13|3
D|Kossounou|Atalanta|4|12|2
D|Helland|Bologna|3|12|2
D|Viery|Fiorentina|6|12|2
D|Joao Mario|Fiorentina|3|12|2
D|Kelly L.|Juventus|5|12|2
D|Veiga D.|Lecce|6|12|3
D|Gallo|Lecce|6|12|3
D|Gaspar K.|Lecce|5|12|3
D|Siebert|Lecce|4|12|2
D|Birindelli|Monza|4|12|3
D|Beukema|Napoli|6|12|2
D|Leysen F.|Sassuolo|6|12|3
D|Fortini|Torino|6|12|2
D|Patterson|Torino|5|12|2
D|Comert|Torino|4|12|2
D|Kamara H.|Udinese|9|12|3
D|Kabasele|Udinese|4|12|3
D|Correia T.|Venezia|5|12|3
D|Hainaut|Venezia|4|12|3
D|Hien|Atalanta|7|11|2
D|Lucchesi|Monza|3|11|3
D|Favasuli|Napoli|4|11|1
D|Balerdi|Roma|6|11|1
D|Van Der Brempt|Sassuolo|2|11|2
D|Palma|Udinese|3|11|2
D|Vitik|Bologna|4|10|2
D|Smolcic I.|Como|4|10|2
D|Parisi|Fiorentina|4|10|2
D|Ranieri L.|Fiorentina|3|10|1
D|Oyono A.|Frosinone|6|10|3
D|Mitaj|Genoa|4|10|3
D|Drameh|Genoa|3|10|2
D|Gatti|Juventus|4|10|2
D|Floriani Mussolini|Lazio|4|10|1
D|Valenti|Parma|4|10|2
D|Britschgi|Parma|3|10|2
D|Ghilardi|Roma|5|10|1
D|Lulli|Roma|2|10|1
D|Walukiewicz|Sassuolo|4|10|2
D|Doig|Sassuolo|5|10|2
D|Bertola|Udinese|4|10|2
D|Zanoli|Udinese|4|10|2
D|Abankwah|Udinese|2|10|1
D|Haps|Venezia|5|10|3
D|Juan Jesus|Venezia|4|10|2
D|Schingtienne|Venezia|3|10|2
D|Halhal|Venezia|3|10|2
D|Mazzocchi|Venezia|1|10|1
D|Carboni A.|Monza|3|9|2
D|Kolasinac|Atalanta|6|8|1
D|Kofler|Cagliari|5|8|2
D|Kambwala|Como|3|8|1
D|Pongracic|Fiorentina|4|8|1
D|Cittadini|Frosinone|4|8|2
D|Terzic|Frosinone|4|8|2
D|Tchato|Frosinone|3|8|2
D|Tomori|Milan|6|8|2
D|Ziolkowski|Monza|1|8|2
D|Marin R.|Napoli|2|8|1
D|Ndiaye|Parma|2|8|2
D|Odenthal|Sassuolo|3|8|1
D|Arizala|Udinese|4|8|1
D|Pellegrini Lu.|Lazio|2|7|1
D|Cande|Sassuolo|3|7|1
D|Sverko|Venezia|3|7|1
D|Franjic|Venezia|3|7|1
D|Alhassane|Bologna|2|6|1
D|Akpoguma|Frosinone|3|6|1
D|Moreno M.|Venezia|4|6|1
D|Casale|Bologna|3|5|1
D|Aurelio|Cagliari|2|5|2
D|Otoa|Genoa|2|5|2
D|Sabelli|Genoa|2|5|2
D|Lazzari|Lazio|2|5|1
D|Ndaba|Lecce|2|5|2
D|Goglichidze|Monza|2|5|2
D|Biraghi|Torino|2|5|1
D|Ebosse|Udinese|3|5|1
D|De Silvestri|Bologna|1|4|1
D|Cabal|Juventus|1|4|1
D|Jean|Lecce|2|4|2
D|Diawara S.|Milan|2|4|1
D|Terracciano F.|Milan|2|4|1
D|Bakoune|Monza|2|4|1
D|Cinquegrano|Sassuolo|2|4|1
D|Sagrado|Venezia|2|4|1
D|Idrissi R.|Cagliari|3|3|1
D|Puczka|Genoa|2|3|1
D|Rugani|Juventus|1|3|1
D|Marianucci|Napoli|1|3|1
D|Carboni F.|Parma|1|3|1
D|Dembele A.|Lecce|1|2|1
D|Antov|Monza|1|2|1
D|Goldaniga|Como|1|1|1
D|Amey|Frosinone|1|1|1
D|Omar Fayed|Frosinone|1|1|1
D|Patric|Lazio|1|1|1
D|Maye|Monza|1|1|1
D|Drobnic|Parma|2|1|1
D|Pieragnolo|Sassuolo|1|1|1
D|Gomes|Venezia|1|1|1
C|Paz N.|Como|29|245|3
C|Calhanoglu|Inter|28|243|3
C|McTominay|Napoli|27|220|3
C|Orsolini|Bologna|25|177|3
C|Pulisic|Milan|24|150|3
C|Rabiot|Milan|23|145|3
C|De Bruyne|Napoli|17|108|3
C|Baturina|Como|20|105|3
C|Mora|Roma|20|100|3
C|Da Cunha|Como|18|87|3
C|Zaccagni|Lazio|16|87|3
C|Barella|Inter|18|81|3
C|Zaniolo|Udinese|18|80|3
C|Atta|Fiorentina|15|78|3
C|Frattesi|Lazio|10|75|3
C|Vlasic|Torino|13|73|3
C|McKennie|Juventus|17|70|3
C|Conceicao|Juventus|13|68|3
C|Ekkelenkamp|Udinese|12|57|3
C|Taylor K.|Lazio|13|53|3
C|Goncalves P.|Fiorentina|12|50|3
C|Mastantuono|Fiorentina|11|50|3
C|Kessie|Atalanta|12|47|3
C|Jones C.|Inter|12|47|3
C|Ederson D.S.|Atalanta|12|46|3
C|Zielinski|Inter|12|45|3
C|Gonzalez N.|Juventus|12|45|3
C|Modric|Milan|12|45|3
C|Moreira|Milan|11|45|3
C|Samardzic|Atalanta|13|44|3
C|Diouf|Inter|9|43|2
C|Alajbegovic|Juventus|11|42|3
C|Kone M.|Roma|10|42|3
C|Zambo Anguissa|Napoli|10|41|3
C|Rowe|Atalanta|10|40|3
C|Gudmundsson A.|Lazio|12|40|3
C|Thorstvedt|Sassuolo|10|39|3
C|Politano|Napoli|9|37|3
C|Saelemaekers|Milan|11|35|2
C|Vergara|Napoli|10|35|2
C|Perrone|Como|10|34|3
C|Bernabe|Parma|7|34|3
C|Locatelli|Juventus|9|33|2
C|Rodriguez Je.|Como|11|31|2
C|Gaetano|Atalanta|7|30|2
C|Milla|Como|6|30|2
C|Cristante|Roma|9|29|3
C|Mbangula|Bologna|8|28|3
C|Njie|Fiorentina|4|28|3
C|Baldanzi|Genoa|11|28|3
C|Bernardeschi|Bologna|10|27|3
C|Calo|Frosinone|8|27|3
C|Casadei|Torino|9|27|3
C|Cambiaghi|Bologna|8|25|3
C|Schmid|Frosinone|8|25|3
C|El Shaarawy|Genoa|7|25|3
C|Thuram K.|Juventus|9|25|2
C|Sarr P.|Juventus|7|25|2
C|Cancellieri|Lazio|9|25|2
C|Hutchinson|Milan|8|25|2
C|Volpato|Sassuolo|9|25|3
C|Cisse A.|Milan|5|24|2
C|Cacciamani|Torino|6|24|3
C|Ferguson|Bologna|7|23|2
C|Fazzini|Cagliari|6|23|3
C|Monteiro J.|Lecce|7|23|3
C|Lobotka|Napoli|8|23|2
C|Mandragora|Torino|8|23|3
C|Pasalic|Atalanta|8|22|2
C|Elmas|Atalanta|7|22|2
C|Ndour|Fiorentina|7|22|2
C|Isaksen|Lazio|9|22|2
C|Chukwueze|Milan|8|22|1
C|Romano|Cagliari|7|21|3
C|Liberali|Como|6|21|2
C|Sucic P.|Inter|9|21|2
C|Fagioli|Fiorentina|7|20|2
C|Pellegrini Lo.|Roma|9|20|3
C|Kone I.|Sassuolo|8|20|3
C|Braganca|Torino|6|20|2
C|Karlstrom|Udinese|7|20|3
C|Frendrup|Genoa|7|19|3
C|Pierotti|Lecce|6|19|3
C|Pisilli|Roma|7|19|2
C|Basic|Venezia|6|19|3
C|Zalewski|Atalanta|7|18|1
C|Oulai|Fiorentina|6|18|2
C|Fitz-Jim|Torino|5|18|2
C|Odgaard|Bologna|8|17|2
C|Caqueret|Como|6|17|1
C|Zhegrova|Juventus|6|17|1
C|Coulibaly L.|Lecce|7|17|3
C|Folorunsho|Monza|4|17|3
C|Ellertsson|Genoa|6|16|3
C|Rovella|Lazio|7|16|2
C|Loftus-Cheek|Milan|4|16|1
C|Nicolussi Caviglia|Parma|6|16|3
C|Adzic|Sassuolo|6|16|3
C|Unai Gomez|Udinese|7|16|3
C|Winks|Cagliari|6|15|3
C|Sow|Genoa|7|15|2
C|Koopmeiners|Juventus|7|15|1
C|Douglas Luiz|Juventus|4|15|1
C|Musah|Milan|3|15|1
C|Colpani|Monza|9|15|3
C|Pessina|Monza|6|15|3
C|Keita M.|Parma|5|15|3
C|Matic|Sassuolo|6|15|2
C|Piotrowski|Udinese|6|15|2
C|Perez K.|Venezia|5|15|3
C|Moro N.|Bologna|4|14|2
C|Toure I.|Monza|6|14|3
C|Bakola|Sassuolo|6|14|2
C|Busio|Venezia|5|14|3
C|Adopo|Cagliari|7|13|3
C|Fini|Frosinone|4|13|3
C|Dele-Bashiru|Lazio|5|13|1
C|Jashari|Milan|5|13|1
C|Pobega|Bologna|6|12|1
C|Massolin|Cagliari|4|12|2
C|Fadera|Cagliari|2|12|2
C|Ricci S.|Como|4|12|1
C|Zerbin|Frosinone|6|12|3
C|Cichella|Frosinone|4|12|2
C|Luis Henrique|Inter|5|12|2
C|Cataldi|Lazio|4|12|1
C|Ngom|Lecce|4|12|3
C|Berisha M.|Lecce|4|12|2
C|Gorter|Lecce|3|12|2
C|Mout|Monza|1|12|2
C|Diallo O.|Parma|3|12|3
C|Dominguez B.|Sassuolo|4|12|2
C|Oristanio|Torino|6|12|2
C|Gineitis|Torino|5|12|1
C|Miller L.|Udinese|4|12|2
C|Brescianini|Fiorentina|3|11|1
C|Koutsoupias|Frosinone|4|11|2
C|Meichtry|Genoa|5|11|2
C|Amorim|Genoa|4|11|2
C|Traore Hj.|Genoa|4|11|1
C|Akinsanmiro|Monza|7|11|2
C|Almqvist|Parma|4|11|2
C|Sohm|Venezia|5|11|3
C|Amondarain|Bologna|5|10|1
C|El Azzouzi O.|Bologna|2|10|1
C|Addai|Como|4|10|1
C|Grillitsch|Frosinone|4|10|2
C|Gandelman|Lecce|4|10|2
C|Ilic|Lecce|1|10|1
C|Gilmour|Napoli|3|10|2
C|Ordonez C.|Parma|3|10|2
C|De Roon|Roma|4|10|2
C|Mkhitaryan|Inter|4|9|1
C|Deiola|Cagliari|3|8|2
C|Gagliardini|Cagliari|3|8|1
C|Masini|Frosinone|3|8|1
C|Messias|Genoa|4|8|1
C|Fabbian|Parma|4|8|2
C|Ilkhan|Torino|4|8|1
C|Fernandez T.|Venezia|3|8|2
C|Felici|Cagliari|5|7|1
C|Stankovic A.|Inter|3|7|1
C|Maleh|Lecce|3|7|1
C|Sulemana I.|Sassuolo|3|7|1
C|Gelli F.|Frosinone|3|6|1
C|Ciurria|Monza|2|6|2
C|Chakvetadze|Udinese|2|6|2
C|Hasa|Frosinone|2|5|1
C|Przyborek|Lazio|1|5|1
C|Boloca|Sassuolo|2|5|1
C|Lipani|Sassuolo|2|5|1
C|Aboukhlal|Torino|3|5|1
C|Jovanovic|Udinese|2|5|1
C|Venturino|Genoa|2|4|1
C|Colombo L.|Monza|3|4|1
C|Anjorin|Torino|1|4|1
C|Zarraga|Udinese|2|4|1
C|Duncan|Venezia|2|4|2
C|Kone B.|Frosinone|1|3|1
C|Belahyane|Lazio|2|3|1
C|Cremaschi|Parma|2|3|1
C|Helgason|Venezia|3|3|2
C|Kaba|Lecce|1|2|1
C|Foe Ondoa|Monza|2|2|1
C|Liteta|Cagliari|1|1|1
C|Ciervo|Cagliari|1|1|1
C|Lahdo|Como|1|1|1
C|El Azzouzi A.|Frosinone|1|1|1
C|Fofana Sa.|Lecce|1|1|1
C|Laerke|Lecce|1|1|1
C|Comotto|Milan|1|1|1
C|Forson O.|Monza|2|1|1
C|Dagasso|Venezia|1|1|1
A|Malen|Roma|38|450|3
A|Martinez L.|Inter|33|361|3
A|Hojlund|Napoli|28|260|3
A|Thuram|Inter|28|249|3
A|Ramos G.|Milan|27|237|3
A|Douvikas|Como|22|185|3
A|Kean|Como|24|183|3
A|Kolo Muani|Juventus|25|165|3
A|Woltemade|Juventus|23|160|3
A|Scamacca|Atalanta|19|110|3
A|Davis K.|Udinese|19|108|3
A|Berardi|Sassuolo|19|106|3
A|Esposito F.P.|Inter|17|105|2
A|Yildiz|Juventus|22|100|2
A|Dybala|Roma|16|100|3
A|Krstovic|Atalanta|18|98|3
A|De Ketelaere|Atalanta|17|95|2
A|Lauriente|Sassuolo|15|83|3
A|Simeone|Torino|14|80|3
A|Raspadori|Atalanta|14|73|2
A|Castro S.|Roma|14|70|2
A|Santos A.|Napoli|14|61|3
A|Pinamonti|Lazio|12|53|3
A|Colombo|Genoa|11|52|3
A|Dovbyk|Bologna|15|51|3
A|Diao|Como|12|50|2
A|Beto|Fiorentina|14|50|3
A|Soule|Roma|13|48|2
A|Pellegrino M.|Fiorentina|14|40|3
A|Varela G.|Monza|7|40|3
A|Esposito Se.|Sassuolo|12|40|2
A|Toure E.|Parma|10|37|3
A|Romero D.|Parma|10|37|3
A|Kevin Carlos|Cagliari|12|36|3
A|Adams A.|Venezia|11|35|3
A|Adams C.|Torino|10|33|3
A|Bowie|Sassuolo|9|32|2
A|Bobcek|Frosinone|9|31|3
A|Piccoli|Bologna|8|29|3
A|Osmajic|Genoa|8|28|3
A|Raimondo|Frosinone|9|27|3
A|Boga|Juventus|7|27|2
A|Yeboah J.|Venezia|9|27|3
A|Gnonto|Fiorentina|7|25|2
A|Kvernadze|Frosinone|6|24|2
A|Ghedjemis|Frosinone|8|23|2
A|Geubbels|Lecce|8|23|3
A|Cutrone|Monza|9|23|3
A|Maldini|Cagliari|5|21|3
A|Camarda|Milan|4|20|3
A|Neres|Napoli|6|20|2
A|Zeballos|Monza|6|18|2
A|Bonny|Inter|7|15|2
A|Fatah|Lecce|4|14|3
A|Lang|Napoli|4|14|2
A|Vitinha O.|Genoa|8|13|2
A|Ngonge|Monza|5|13|2
A|Rrahmani Al.|Venezia|7|13|2
A|Mendy P.|Cagliari|4|12|2
A|N'Dri|Lecce|4|12|2
A|Lucca|Napoli|4|12|1
A|Zapata D.|Torino|6|12|2
A|Birligea|Frosinone|5|11|1
A|Stulic|Lecce|6|11|2
A|Elphege|Parma|3|11|2
A|Lontani|Parma|3|11|2
A|Nzola|Cagliari|4|10|2
A|Milik|Juventus|4|10|1
A|Ekhator|Juventus|3|10|1
A|Borrelli|Cagliari|4|9|1
A|Kulenovic|Torino|4|9|2
A|Sulemana K.|Atalanta|6|8|1
A|Noslin|Lazio|6|8|3
A|Mota|Monza|4|8|1
A|Adorante|Venezia|4|8|2
A|Giovane|Napoli|4|7|1
A|Gueye|Udinese|4|7|3
A|Frigan|Parma|4|6|1
A|Havel|Genoa|4|5|2
A|Robinson J.|Monza|4|5|1
A|Enem|Bologna|2|4|2
A|Robinho Junior|Genoa|1|3|1
A|Bayo V.|Udinese|1|3|2
A|Trepy|Cagliari|1|2|1
A|De Martis|Parma|1|1|1
A|Lisman|Venezia|1|1|1
A|Lauberbach|Venezia|1|1|1""".strip()

ROLES = ["P", "D", "C", "A"]
ROLE_NAME = {"P": "Portieri", "D": "Difensori", "C": "Centrocampisti", "A": "Attaccanti"}
ROLE_ONE = {"P": "Portiere", "D": "Difensore", "C": "Centrocampista", "A": "Attaccante"}
TIER_MULT = {"Big": 1.28, "Semi": 1.13, "Titolare": 1.0, "Low": 0.9, "Slot": 0.82}
TIT_MULT = {3: 1.0, 2: 0.72, 1: 0.42}
TIT_CAP = {3: 1.0, 2: 0.90, 1: 0.70}
TIT_LABEL = {3: "titolare", 2: "ballottaggio", 1: "riserva"}

MODULI = {
    "3-4-3": {"D": 3, "C": 4, "A": 3}, "3-5-2": {"D": 3, "C": 5, "A": 2},
    "4-3-3": {"D": 4, "C": 3, "A": 3}, "4-4-2": {"D": 4, "C": 4, "A": 2},
    "4-5-1": {"D": 4, "C": 5, "A": 1}, "5-3-2": {"D": 5, "C": 3, "A": 2},
    "5-4-1": {"D": 5, "C": 4, "A": 1},
}

PRESETS = {
    "equilibrata":  {"label": "Equilibrata",         "alloc": {"P": 7, "D": 17, "C": 30, "A": 46},
                     "note": "Nessun buco, nessuna stella. Regge bene le aste imprevedibili."},
    "spaccata":     {"label": "Attacco spaccato",    "alloc": {"P": 5, "D": 12, "C": 23, "A": 60},
                     "note": "Due-tre bomber veri, resto low cost. Alta varianza, altissimo tetto."},
    "modificatore": {"label": "Modificatore difesa", "alloc": {"P": 12, "D": 30, "C": 30, "A": 28},
                     "note": "Difesa titolarissima e portiere top. Punti garantiti ogni giornata."},
    "centrocampo":  {"label": "Centrocampo pesante", "alloc": {"P": 6, "D": 16, "C": 42, "A": 36},
                     "note": "I centrocampisti da bonus costano meno degli attaccanti pari resa."},
    "gaudio":       {"label": "Fondi su 4 big",      "alloc": {"P": 5, "D": 15, "C": 32, "A": 48},
                     "note": "Quattro top assoluti presi a ogni costo, resto rosa a 1-5 crediti."},
}


# ------------------------------------------------------------------
#  LISTONE
# ------------------------------------------------------------------
def parse_raw(raw):
    out = []
    for i, line in enumerate(raw.split("\n")):
        line = line.strip()
        if not line:
            continue
        c = line.split("|")
        if len(c) < 4:
            continue
        out.append({"id": "p%d" % i, "r": c[0].strip().upper(), "nome": c[1].strip(),
                    "team": c[2].strip(), "q": int(float(c[3])),
                    "fvm": int(float(c[4])) if len(c) > 4 and c[4].strip() else 0,
                    "t": int(c[5]) if len(c) > 5 and c[5].strip() else 2})
    return out


def assign_tiers(players):
    out = []
    for r in ROLES:
        arr = sorted([p for p in players if p["r"] == r], key=lambda x: -(x.get("fvm") or x["q"]))
        n = max(1, len(arr) - 1)
        for i, p in enumerate(arr):
            pc = i / n
            q = dict(p)
            q["tier"] = ("Big" if pc <= 0.06 else "Semi" if pc <= 0.18 else
                         "Titolare" if pc <= 0.45 else "Low" if pc <= 0.75 else "Slot")
            out.append(q)
    return out


def clamp(v, a, b):
    return max(a, min(b, v))


def cr(x):
    return max(1, int(round(x)))


# ------------------------------------------------------------------
#  STATO
# ------------------------------------------------------------------
def default_state():
    return {
        "cfg": {"teams": 10, "budget": 500, "slots": {"P": 3, "D": 8, "C": 8, "A": 6},
                "mod_difesa": True, "names": []},
        "alloc": dict(PRESETS["equilibrata"]["alloc"]),
        "preset": "equilibrata",
        "players": assign_tiers(parse_raw(RAW)),
        "sold": {},          # player_id -> {"buyer": idx, "price": n}
        "targets": {},       # player_id -> 0..3
        "parts": None,
        "formation": {"modulo": "3-4-3", "slots": {}},
        "chat": [],
        "api_key": "",
    }


STATE = default_state()
LOCK = threading.Lock()


def load_state():
    global STATE
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                s = json.load(f)
            base = default_state()
            base.update(s)
            # il listone segue sempre la versione dello script
            if len(base.get("players") or []) != len(default_state()["players"]):
                base["players"] = default_state()["players"]
                base["sold"], base["targets"] = {}, {}
                base["formation"] = {"modulo": "3-4-3", "slots": {}}
                if base.get("parts"):
                    base["parts"] = None
                print("  (listone diverso: asta precedente azzerata)")
            STATE = base
            sync_parts()
        except Exception as e:
            print("Stato non leggibile, riparto da zero:", e)


def save_state():
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(STATE, f, ensure_ascii=False)
    except Exception as e:
        print("Salvataggio non riuscito:", e)


def sync_parts():
    """I contatori delle squadre si ricavano SEMPRE dagli acquisti registrati.
    Cosi' crediti, slot e spesa non possono restare disallineati dalle rose."""
    st = STATE
    if not st.get("parts"):
        return
    cfg = st["cfg"]
    for pt in st["parts"]:
        pt["credits"] = cfg["budget"]
        pt["filled"] = {r: 0 for r in ROLES}
        pt["spent"] = {r: 0 for r in ROLES}
    for pid, s in list(st["sold"].items()):
        p = next((x for x in st["players"] if x["id"] == pid), None)
        if not p or not isinstance(s.get("buyer"), int) or s["buyer"] >= len(st["parts"]):
            st["sold"].pop(pid, None)          # acquisto orfano: via
            continue
        pt = st["parts"][s["buyer"]]
        pt["credits"] -= s["price"]
        pt["filled"][p["r"]] = pt["filled"].get(p["r"], 0) + 1
        pt["spent"][p["r"]] = pt["spent"].get(p["r"], 0) + s["price"]
    # in campo restano solo i giocatori che ho davvero in rosa
    f = st.get("formation") or {"modulo": "3-4-3", "slots": {}}
    miei = {k for k, v in st["sold"].items() if v["buyer"] == 0}
    f["slots"] = {k: v for k, v in (f.get("slots") or {}).items() if v in miei}
    st["formation"] = f


def fresh_parts():
    cfg = STATE["cfg"]
    names = cfg.get("names") or []
    out = []
    for i in range(cfg["teams"]):
        nm = names[i] if i < len(names) and names[i] else ("La mia squadra" if i == 0 else "Squadra %d" % (i + 1))
        out.append({"name": nm, "credits": cfg["budget"],
                    "filled": {r: 0 for r in ROLES}, "spent": {r: 0 for r in ROLES}})
    return out


# ------------------------------------------------------------------
#  MOTORE
# ------------------------------------------------------------------
class Engine:
    def __init__(self, st):
        cfg = self.cfg = st["cfg"]
        self.alloc, self.sold, self.targets = st["alloc"], st["sold"], st["targets"]
        self.parts, self.players = st["parts"], st["players"]
        self.avail = [p for p in self.players if p["id"] not in self.sold]

        self.total_credits = sum(p["credits"] for p in self.parts)
        self.slots_left = {r: sum(max(0, cfg["slots"][r] - p["filled"].get(r, 0)) for p in self.parts)
                           for r in ROLES}

        pool = []
        for r in ROLES:
            arr = sorted([p for p in self.avail if p["r"] == r], key=lambda x: -(x.get("fvm") or x["q"]))
            pool += arr[: self.slots_left[r]]
        self.pool = pool
        self.pool_ids = set(p["id"] for p in pool)

        self.gamma = 1.0  # l'FVM e' gia' una valutazione di mercato: non va concentrata oltre
        self.raw_sum = sum(self.raw(p) for p in pool) or 1
        self.slots_tot_left = sum(self.slots_left.values())
        self.free = max(0, self.total_credits - self.slots_tot_left)

        full = []
        for r in ROLES:
            arr = sorted([p for p in self.players if p["r"] == r], key=lambda x: -(x.get("fvm") or x["q"]))
            full += arr[: cfg["slots"][r] * cfg["teams"]]
        ref = (cfg["budget"] * cfg["teams"]) / (sum(p["q"] for p in full) or 1)
        now = self.total_credits / (sum(p["q"] for p in pool) or 1)
        self.factor = now / ref if ref else 1.0

        self.marginal = {}
        for r in ROLES:
            arr = [p for p in pool if p["r"] == r]
            self.marginal[r] = self.price(arr[-1]) if arr else 1

        self.caps = []
        for i, pt in enumerate(self.parts):
            left = sum(max(0, cfg["slots"][r] - pt["filled"].get(r, 0)) for r in ROLES)
            self.caps.append({"i": i, "name": pt["name"], "credits": pt["credits"], "left": left,
                              "cap": max(1, pt["credits"] - max(0, left - 1)),
                              "medio": round(pt["credits"] / left, 1) if left else 0,
                              "filled": pt["filled"],
                              "scoperti": [r for r in ROLES if pt["filled"].get(r, 0) < cfg["slots"][r]]})

        self.me = self.parts[0]
        my_filled = sum(self.me["filled"].get(r, 0) for r in ROLES)
        self.my_slots_left = sum(cfg["slots"][r] for r in ROLES) - my_filled

        self.role_budget, self.role_spent, self.role_left = {}, {}, {}
        for r in ROLES:
            self.role_budget[r] = self.alloc[r] / 100.0 * cfg["budget"]
            self.role_spent[r] = self.me["spent"].get(r, 0)
            self.role_left[r] = self.role_budget[r] - self.role_spent[r]
        self.flex = self.me["credits"] - sum(max(0, self.role_left[r]) for r in ROLES)

    def raw(self, p):
        # FVM = fantavalore di mercato del listone ufficiale: incorpora gia' titolarita' e ruolo.
        v = p.get("fvm")
        if not v:
            v = p["q"] * TIER_MULT[p["tier"]] * TIT_MULT.get(p.get("t", 2), 0.72) * 4
        return v ** self.gamma

    def price(self, p):
        return cr(1 + self.free * self.raw(p) / self.raw_sum)

    def evaluate(self, p):
        cfg = self.cfg
        base = self.price(p)
        r = p["r"]
        mine = max(0, cfg["slots"][r] - self.me["filled"].get(r, 0))
        stars = self.targets.get(p["id"], 0)
        boost = [1, 1.08, 1.18, 1.32][stars]
        same_tier = len([x for x in self.avail if x["r"] == r and x["tier"] == p["tier"]])
        needing = len([pt for pt in self.parts if pt["filled"].get(r, 0) < cfg["slots"][r]])
        scarcity = clamp(needing / max(1, same_tier), 0.6, 1.6)

        rivals = [c for c in self.caps if c["i"] != 0 and c["filled"].get(r, 0) < cfg["slots"][r]]
        top_rival = max([c["cap"] for c in rivals]) if rivals else 0
        top_name = next((c["name"] for c in rivals if c["cap"] == top_rival), None)
        contenders = len([c for c in rivals if c["cap"] >= base])
        pressure = clamp(0.90 + 0.04 * contenders, 0.90, 1.15)

        altri = sum(max(0, cfg["slots"][r2] - self.me["filled"].get(r2, 0)) * self.marginal[r2]
                    for r2 in ROLES if r2 != r)
        riserva_ruolo = max(0, mine - 1) * self.marginal[r]
        afford_hard = self.me["credits"] - altri - riserva_ruolo
        afford_role = max(0, self.role_left[r]) + max(0, self.flex) * 0.55 - riserva_ruolo
        ratio = clamp(afford_role / max(1, base), 0.2, 3.0)

        tit = p.get("t", 2)
        voglia = base * boost * (0.88 + 0.12 * scarcity) * pressure * TIT_CAP.get(tit, 0.9)
        hard_cap = self.me["credits"] - max(0, self.my_slots_left - 1)
        beat = top_rival + 1 if rivals else 1
        mx = min(voglia, afford_role, afford_hard, hard_cap, beat)
        if mine == 0:
            mx = min(mx, 1)
        mx = cr(max(1, mx))
        mn = min(cr(base * 0.72), mx)

        return {"base": base, "min": mn, "max": mx, "tit": tit, "tit_label": TIT_LABEL.get(tit, ""),
                "ratio": round(ratio, 2), "scarcity": round(scarcity, 2), "same_tier": same_tier,
                "needing": needing, "hard_cap": cr(hard_cap), "top_rival": top_rival,
                "top_rival_name": top_name, "contenders": contenders, "rivals_count": len(rivals),
                "beat": beat, "mine_left": mine, "in_pool": p["id"] in self.pool_ids}


# ------------------------------------------------------------------
#  FASE D'ASTA, AVVISI, PAGELLE
# ------------------------------------------------------------------
def phase_suggested(e):
    """L'asta va per ruoli: il primo non ancora esaurito in lega."""
    cfg = STATE["cfg"]
    for r in ROLES:
        if e.slots_left[r] > 0:
            return r
    return "A"


def alerts(e):
    """Avvisi: ultimo titolare disponibile per ruolo, e reparti in emergenza."""
    out = []
    cfg = STATE["cfg"]
    for r in ROLES:
        tit = [p for p in e.avail if p["r"] == r and p.get("t") == 3]
        needing = len([pt for pt in e.parts if pt["filled"].get(r, 0) < cfg["slots"][r]])
        mine = max(0, cfg["slots"][r] - e.me["filled"].get(r, 0))
        if mine > 0 and 0 < len(tit) <= 3:
            best = sorted(tit, key=lambda x: -(x.get("fvm") or x["q"]))[0]
            out.append({"lvl": "alto" if len(tit) == 1 else "medio",
                        "txt": "Restano %d titolari tra i %s e %d squadre devono ancora comprarne. "
                               "Il migliore libero e' %s (%s), prezzo %d."
                               % (len(tit), ROLE_NAME[r].lower(), needing, best["nome"], best["team"], e.price(best))})
        if mine > 0 and len(tit) == 0:
            out.append({"lvl": "alto",
                        "txt": "Finiti i titolari tra i %s: da qui in poi si compra solo ballottaggio o riserva."
                               % ROLE_NAME[r].lower()})
    # squadra troppo concentrata
    mie = [next((x for x in e.players if x["id"] == k), None) for k, v in STATE["sold"].items() if v["buyer"] == 0]
    mie = [x for x in mie if x]
    conteggio = {}
    for p in mie:
        conteggio[p["team"]] = conteggio.get(p["team"], 0) + 1
    for team, n in sorted(conteggio.items(), key=lambda x: -x[1]):
        if n >= 4:
            out.append({"lvl": "medio", "txt": "Hai %d giocatori del %s: un turnover o una giornata storta "
                                               "ti azzera mezza formazione." % (n, team)})
            break
    return out


def ref_price_fn(e):
    """Prezzo di mercato di un giocatore a inizio asta: il metro per giudicare la spesa."""
    cfg = e.cfg
    full = []
    for r in ROLES:
        arr = sorted([p for p in e.players if p["r"] == r], key=lambda x: -(x.get("fvm") or x["q"]))
        full += arr[: cfg["slots"][r] * cfg["teams"]]
    tot = sum((p.get("fvm") or p["q"] * 4) for p in full) or 1
    slots_tot = sum(cfg["slots"][r] for r in ROLES) * cfg["teams"]
    libero = max(0, cfg["budget"] * cfg["teams"] - slots_tot)
    return lambda p: 1 + libero * (p.get("fvm") or p["q"] * 4) / tot


def pagelle(e):
    """Chi sta spendendo bene: valore di mercato acquistato per credito speso."""
    refp = ref_price_fn(e)
    out = []
    for i, pt in enumerate(e.parts):
        ids = [k for k, v in STATE["sold"].items() if v["buyer"] == i]
        speso = sum(STATE["sold"][k]["price"] for k in ids)
        atteso = 0
        for k in ids:
            p = next((x for x in e.players if x["id"] == k), None)
            if p:
                atteso += refp(p)
        idx = (atteso / speso) if speso > 0 else None
        out.append({"i": i, "name": pt["name"], "giocatori": len(ids), "speso": speso,
                    "valore": round(atteso), "indice": round(idx, 2) if idx else None,
                    "giudizio": ("" if idx is None else
                                 "sta comprando bene" if idx >= 1.12 else
                                 "sta pagando troppo" if idx <= 0.88 else "in linea col mercato")})
    return out


ALT_W = [1.0, 0.7, 0.45, 0.25]   # vice di squadra > equivalente > ruolo scoperto > occasione


def alternatives(bought, n=5):
    """Cosa comprare adesso, in ordine di priorita'."""
    e = Engine(STATE)
    cfg = e.cfg
    mine_left = {r: max(0, cfg["slots"][r] - e.me["filled"].get(r, 0)) for r in ROLES}
    fb = bought.get("fvm") or bought["q"]
    same = sorted([x for x in e.avail if x["team"] == bought["team"] and x["r"] == bought["r"]],
                  key=lambda x: -(x.get("fvm") or x["q"]))
    vice_id = same[0]["id"] if same else None

    out = []
    for p in e.avail:
        r = p["r"]
        if mine_left[r] <= 0:
            continue
        ev = e.evaluate(p)
        if ev["max"] < 1:
            continue
        s1 = 1.0 if p["id"] == vice_id else (0.55 if p["team"] == bought["team"] and r == bought["r"] else 0.0)
        fp = p.get("fvm") or p["q"]
        s2 = max(0.0, 1 - abs(fp - fb) / max(fp, fb, 1)) if (r == bought["r"] and p["team"] != bought["team"]) else 0.0
        s3 = mine_left[r] / max(1, cfg["slots"][r])
        beat = min(ev["beat"], ev["base"])
        s4 = max(0.0, (ev["base"] - beat) / max(1, ev["base"]))
        score = ALT_W[0] * s1 + ALT_W[1] * s2 + ALT_W[2] * s3 + ALT_W[3] * s4
        if p["id"] == vice_id:
            why = "eredita il posto di %s al %s" % (bought["nome"], bought["team"])
        elif s1 > 0:
            why = "stesso reparto del %s" % bought["team"]
        elif s2 > 0.8:
            why = "stesso rendimento atteso di %s, prezzo simile" % bought["nome"]
        elif s4 > 0.25:
            why = "pochi rivali possono spingerlo: lo chiudi a %d" % beat
        elif s3 > 0.6:
            why = "%s: il tuo reparto piu' scoperto" % ROLE_NAME[r].lower()
        else:
            why = "alternativa di pari fascia"
        out.append({"id": p["id"], "nome": p["nome"], "team": p["team"], "r": r,
                    "tit": ev["tit_label"], "tit_n": ev["tit"], "base": ev["base"],
                    "max": ev["max"], "why": why, "score": round(score, 3)})
    out.sort(key=lambda x: -x["score"])
    return out[:n]


# ------------------------------------------------------------------
#  SNAPSHOT
# ------------------------------------------------------------------
def snapshot():
    st = STATE
    if not st["parts"]:
        return {"ready": False, "cfg": st["cfg"], "alloc": st["alloc"], "preset": st["preset"],
                "presets": PRESETS, "n_players": len(st["players"]), "has_key": bool(st["api_key"]),
                "version": VERSION}
    e = Engine(st)
    lista = []
    for p in st["players"]:
        s = st["sold"].get(p["id"])
        row = {"id": p["id"], "r": p["r"], "nome": p["nome"], "team": p["team"], "q": p["q"],
               "fvm": p.get("fvm", 0), "t": p.get("t", 2), "tier": p["tier"],
               "stars": st["targets"].get(p["id"], 0)}
        if s:
            row["buyer"] = s["buyer"]
            row["buyer_name"] = st["parts"][s["buyer"]]["name"]
            row["paid"] = s["price"]
        else:
            ev = e.evaluate(p)
            row["base"] = ev["base"]
            row["max"] = ev["max"]
        lista.append(row)
    lista.sort(key=lambda x: (ROLES.index(x["r"]), -(x.get("fvm") or x["q"])))

    rose = {}
    for pid, s in st["sold"].items():
        pl = next((x for x in st["players"] if x["id"] == pid), None)
        if pl:
            rose.setdefault(str(s["buyer"]), []).append(
                {"id": pl["id"], "r": pl["r"], "nome": pl["nome"], "team": pl["team"],
                 "t": pl.get("t", 2), "fvm": pl.get("fvm", 0), "price": s["price"]})
    for k in rose:
        rose[k].sort(key=lambda x: (ROLES.index(x["r"]), -x["price"]))

    return {
        "ready": True, "version": VERSION, "cfg": st["cfg"], "alloc": st["alloc"],
        "preset": st["preset"], "presets": PRESETS, "has_key": bool(st["api_key"]),
        "parts": st["parts"], "caps": e.caps, "players": lista, "rose": rose,
        "inflation": round(e.factor, 2), "flex": int(round(e.flex)),
        "my_slots_left": e.my_slots_left, "slots_left": e.slots_left,
        "role_budget": {r: int(round(e.role_budget[r])) for r in ROLES},
        "role_spent": {r: int(round(e.role_spent[r])) for r in ROLES},
        "phase": phase_suggested(e), "alerts": alerts(e), "pagelle": pagelle(e),
        "formation": st.get("formation", {"modulo": "3-4-3", "slots": {}}),
        "moduli": MODULI, "chat": st.get("chat", [])[-40:], "n_players": len(st["players"]),
        "venduti": len(st["sold"]),
    }


# ------------------------------------------------------------------
#  AGENTI
# ------------------------------------------------------------------
def call_claude(system, messages, use_search=False, max_tokens=1200):
    key = STATE.get("api_key", "")
    if not key:
        raise RuntimeError("Nessuna chiave API salvata. L'asta funziona lo stesso: gli agenti sono un extra.")
    body = {"model": "claude-sonnet-4-6", "max_tokens": max_tokens,
            "system": system, "messages": messages}
    if use_search:
        body["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={"content-type": "application/json", "x-api-key": key,
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    return "\n".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")


def parse_json(txt):
    clean = re.sub(r"```json|```", "", txt).strip()
    a, b = clean.find("{"), clean.rfind("}")
    return json.loads(clean[a:b + 1] if a >= 0 else clean)


def stato_asta(e, compatto=False):
    """Il quadro che gli agenti leggono."""
    st = STATE
    top = {}
    for r in ROLES:
        arr = sorted([p for p in e.avail if p["r"] == r], key=lambda x: -(x.get("fvm") or x["q"]))[:8]
        top[r] = ["%s (%s) %s q%d -> ~%dcr" % (p["nome"], p["team"], TIT_LABEL.get(p.get("t", 2), ""),
                                               p["q"], e.price(p)) for p in arr]
    mia = [{"nome": x["nome"], "team": x["team"], "r": x["r"], "pagato": STATE["sold"][x["id"]]["price"]}
           for x in e.players if x["id"] in STATE["sold"] and STATE["sold"][x["id"]]["buyer"] == 0]
    d = {
        "formato": {"squadre": st["cfg"]["teams"], "budget": st["cfg"]["budget"],
                    "rosa": st["cfg"]["slots"], "modificatore_difesa": st["cfg"]["mod_difesa"]},
        "fase_asta": ROLE_NAME[phase_suggested(e)],
        "strategia_attuale": st["alloc"],
        "mia_situazione": {"crediti": e.me["credits"], "slot_riempiti": e.me["filled"],
                           "spesa_per_ruolo": e.me["spent"], "scostamento_dal_piano": int(round(e.flex)),
                           "rosa": mia},
        "avversari": [{"nome": c["name"], "crediti": c["credits"], "slot_presi": c["filled"],
                       "offerta_massima_su_un_nome": c["cap"], "ruoli_scoperti": c["scoperti"]}
                      for c in e.caps[1:]],
        "inflazione_mercato": round(e.factor, 2),
        "avvisi": [a["txt"] for a in alerts(e)],
        "top_disponibili": top,
    }
    if not compatto:
        d["miei_obiettivi"] = [next((p["nome"] for p in st["players"] if p["id"] == k), "") + " " + "*" * v
                               for k, v in st["targets"].items() if v > 0 and k not in st["sold"]][:12]
    return d


SYS_STRATEGA = (
    "Sei un fantallenatore italiano con 15 anni di aste alle spalle. Ragioni per crediti, non per simpatie.\n"
    "Conosci: inflazione d'asta, scarsita' di ruolo, modificatore difesa, il rischio dei buchi di rosa,\n"
    "il fatto che chi resta con troppi crediti a fine asta ha perso valore.\n"
    "L'asta va per ruoli in ordine: portieri, difensori, centrocampisti, attaccanti. Tieni conto della fase.\n"
    "Ragiona sempre in funzione degli avversari: chi e' rimasto liquido e' una minaccia, chi ha chiuso un ruolo\n"
    "non ti contende piu' quei giocatori, e i ruoli che quasi nessuno deve piu' coprire si comprano al minimo.\n"
    "Se un avversario ricco ha un solo ruolo scoperto, prevedi dove spendera' e chiamalo per nome.\n"
    "Rispondi SOLO con JSON valido, nessun markdown. Schema:\n"
    '{"fase":"...","lettura":"2 frasi","alloc":{"P":n,"D":n,"C":n,"A":n},"perche_alloc":"1 frase",'
    '"mosse":["3 azioni concrete con nomi e cifre"],"rischio":"il pericolo numero uno adesso"}\n'
    "alloc deve sommare 100."
)


def agent_strategist():
    e = Engine(STATE)
    txt = call_claude(SYS_STRATEGA,
                      [{"role": "user", "content": "Stato dell'asta:\n" + json.dumps(stato_asta(e), ensure_ascii=False, indent=1)}])
    j = parse_json(txt)
    al = j.get("alloc")
    if al and abs(sum(al.get(r, 0) for r in ROLES) - 100) < 3:
        STATE["alloc"] = {r: int(al[r]) for r in ROLES}
        STATE["preset"] = "custom"
        save_state()
    return j


def agent_scout(player_id, news=False):
    st = STATE
    e = Engine(st)
    p = next((x for x in st["players"] if x["id"] == player_id), None)
    if not p:
        raise RuntimeError("Giocatore non trovato.")
    ev = e.evaluate(p)
    system = (
        "Sei un analista di quotazioni per il fantacalcio italiano. Valuti un giocatore per un'asta Classic:\n"
        "titolarita' attesa, rigori, calci piazzati, bonus attesi, minutaggio, continuita', rischio infortuni,\n"
        "peso nel modulo. Sei brutalmente onesto: se un nome e' sopravvalutato lo dici.\n"
        "Rispondi SOLO con JSON valido, nessun markdown. Schema:\n"
        '{"giudizio":"2-3 frasi","fantamedia_attesa":"es. 6.4-6.9","punti_forza":["max 3"],"rischi":["max 3"],'
        '"valore_equo":n,"prezzo_massimo":n,"verdetto":"prendere|prendere se scende|lasciare"}\n'
        "valore_equo e prezzo_massimo in crediti su un budget da %d." % st["cfg"]["budget"]
        + (" Usa la ricerca web per notizie recenti su squadra, infortuni e formazioni." if news else "")
    )
    user = ("Giocatore: %s - %s - ruolo %s - quotazione ufficiale %d - fantavalore di mercato %d - %s.\n"
            "Asta: %d squadre, budget %d, fase %s. Prezzo calcolato %d crediti.\n"
            "Mi restano %d crediti e %d slot. Strategia: %d/%d/%d/%d su P/D/C/A."
            % (p["nome"], p["team"], p["r"], p["q"], p.get("fvm", 0), TIT_LABEL.get(p.get("t", 2), ""),
               st["cfg"]["teams"], st["cfg"]["budget"], ROLE_NAME[phase_suggested(e)], ev["base"],
               e.me["credits"], e.my_slots_left,
               st["alloc"]["P"], st["alloc"]["D"], st["alloc"]["C"], st["alloc"]["A"]))
    j = parse_json(call_claude(system, [{"role": "user", "content": user}], news))
    j["player"] = player_id
    return j


SYS_CHAT = (
    "Sei il consulente d'asta di un fantallenatore, seduto accanto a lui mentre l'asta e' in corso.\n"
    "Sei specializzato in fantacalcio italiano Classic: quotazioni, fantamedia, bonus e malus, rigoristi,\n"
    "calci piazzati, modificatore di difesa, ballottaggi, turnover da coppe, rischio infortuni,\n"
    "dinamiche d'asta (inflazione, scarsita' di ruolo, aste al rialzo, il valore di restare liquidi).\n"
    "Hai davanti lo stato aggiornato dell'asta: usalo, cita nomi e cifre concrete, niente genericita'.\n"
    "Rispondi in italiano, breve e diretto: 2-6 frasi, o un elenco secco quando servono piu' nomi.\n"
    "Se ti chiede se prendere un giocatore, dai una cifra massima e una motivazione in una riga.\n"
    "Se una cosa non la sai (una notizia di oggi, un infortunio dell'ultima ora) dillo invece di inventarla.\n"
    "Non sei un tifoso: se sta per fare una sciocchezza glielo dici."
)


def agent_chat(msg):
    st = STATE
    e = Engine(st)
    st.setdefault("chat", []).append({"role": "user", "content": msg})
    save_state()                      # la domanda resta scritta comunque
    storia = [m for m in st["chat"] if m.get("role") in ("user", "assistant") and not m.get("err")][-12:]
    contesto = ("Stato dell'asta in questo momento:\n"
                + json.dumps(stato_asta(e, compatto=True), ensure_ascii=False, indent=1))
    msgs = [{"role": "user", "content": contesto + "\n\nDomanda: " + storia[-1]["content"]}] \
        if len(storia) == 1 else \
        ([{"role": m["role"], "content": m["content"]} for m in storia[:-1]]
         + [{"role": "user", "content": contesto + "\n\nDomanda: " + storia[-1]["content"]}])
    try:
        risp = call_claude(SYS_CHAT, msgs, max_tokens=900).strip()
    except Exception as ex:
        st["chat"].append({"role": "assistant", "content": "Non riesco a rispondere: %s" % ex, "err": True})
        st["chat"] = st["chat"][-60:]
        save_state()
        return {"errore": str(ex)}
    st["chat"].append({"role": "assistant", "content": risp})
    st["chat"] = st["chat"][-60:]
    save_state()
    return {"risposta": risp}


def import_listone(text):
    out, k = [], 0
    for line in text.strip().split("\n"):
        cols = [c.strip().strip('"') for c in re.split(r"[;,\t]", line)]
        if len(cols) < 3:
            continue
        ri = next((i for i, c in enumerate(cols) if re.fullmatch(r"[PpDdCcAa]", c)), None)
        if ri is None:
            continue
        nome_i = next((i for i, c in enumerate(cols)
                       if i > ri and c and not c.replace(".", "").isdigit() and len(c) > 2), None)
        if nome_i is None:
            continue
        team_i = next((i for i, c in enumerate(cols)
                       if i > nome_i and c and not c.replace(".", "").isdigit() and len(c) > 1), None)
        nums = [float(c) for i, c in enumerate(cols)
                if i > ri and re.fullmatch(r"\d+(\.\d+)?", c) and 0 < float(c) < 1200]
        if not nums:
            continue
        k += 1
        out.append({"id": "i%d" % k, "r": cols[ri].upper(), "nome": cols[nome_i],
                    "team": cols[team_i] if team_i is not None else "?",
                    "q": int(nums[0]), "fvm": int(nums[3]) if len(nums) > 3 else 0, "t": 2})
    if len(out) > 20:
        STATE["players"] = assign_tiers(out)
        STATE["sold"], STATE["targets"] = {}, {}
        STATE["formation"] = {"modulo": "3-4-3", "slots": {}}
        sync_parts()
        save_state()
        return len(out)
    return 0


# ------------------------------------------------------------------
#  AZIONI
# ------------------------------------------------------------------
def do_assign(player_id, buyer, price):
    st = STATE
    p = next((x for x in st["players"] if x["id"] == player_id), None)
    if not p or player_id in st["sold"]:
        return
    price = max(1, int(price))
    st["sold"][player_id] = {"buyer": int(buyer), "price": price}
    pt = st["parts"][int(buyer)]
    pt["credits"] -= price
    pt["filled"][p["r"]] = pt["filled"].get(p["r"], 0) + 1
    pt["spent"][p["r"]] = pt["spent"].get(p["r"], 0) + price
    save_state()


def do_undo(player_id):
    st = STATE
    s = st["sold"].pop(player_id, None)
    if not s:
        return
    p = next((x for x in st["players"] if x["id"] == player_id), None)
    if not p:
        return
    pt = st["parts"][s["buyer"]]
    pt["credits"] += s["price"]
    pt["filled"][p["r"]] = max(0, pt["filled"].get(p["r"], 0) - 1)
    pt["spent"][p["r"]] = max(0, pt["spent"].get(p["r"], 0) - s["price"])
    # se era schierato, liberalo dal campo
    f = st.get("formation", {}).get("slots", {})
    for k in [k for k, v in f.items() if v == player_id]:
        f.pop(k, None)
    save_state()

# ------------------------------------------------------------------
#  INTERFACCIA
# ------------------------------------------------------------------
PAGE = r"""<!doctype html><html lang="it"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0E141A">
<title>Banco d'asta</title>
<style>
:root{--ink:#0E141A;--panel:#151F27;--panel2:#1B2831;--line:#2A3B47;--rosa:#F2A7B3;--cream:#EDE8E2;
--mut:#8CA0AF;--mint:#57D9A3;--amber:#F5B851;--red:#FF6B6B}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%}
body{margin:0;background:var(--ink);color:var(--cream);overflow:hidden;
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;-webkit-font-smoothing:antialiased}
h1,h3{font-family:'Archivo Black','Arial Black',Impact,sans-serif;letter-spacing:-.02em;margin:0;text-transform:uppercase}
.mono{font-family:ui-monospace,'SF Mono',Menlo,monospace;font-variant-numeric:tabular-nums}

.shell{display:grid;grid-template-columns:330px 1fr;height:100vh;height:100dvh}
.shell.solo{grid-template-columns:1fr}   /* prima di aprire l'asta il listone non esiste */
.side{border-right:1px solid var(--line);display:flex;flex-direction:column;min-height:0;background:#111922}
.main{display:flex;flex-direction:column;min-height:0}
.mainScroll{overflow:auto;padding:14px 18px 40px;flex:1}
@media(max-width:900px){.shell{grid-template-columns:1fr}
 .side{position:fixed;inset:0;z-index:50;display:none}.side.open{display:flex}
 .sideToggle{display:inline-flex!important}}
.sideToggle{display:none}

.sHead{padding:calc(10px + env(safe-area-inset-top)) 14px 10px;border-bottom:1px solid var(--line)}
.sList{overflow:auto;flex:1;padding:0 14px 30px}
.topbar{display:flex;align-items:center;gap:12px;padding:calc(10px + env(safe-area-inset-top)) 18px 10px;
border-bottom:1px solid var(--line);flex-wrap:wrap}
.brand{display:flex;align-items:baseline;gap:8px}.brand h1{font-size:17px}
.brand span{font-size:9px;letter-spacing:.16em;color:var(--rosa)}
nav{display:flex;gap:6px;overflow-x:auto;flex:1}nav::-webkit-scrollbar{display:none}
nav button{flex:0 0 auto;background:none;border:1px solid var(--line);color:var(--mut);padding:7px 13px;
border-radius:999px;font-size:12.5px;font-weight:600;font-family:inherit}
nav button.on{background:var(--rosa);border-color:var(--rosa);color:#12181D}
.cash{text-align:right;line-height:1.1}.cash b{font-family:ui-monospace,Menlo,monospace;font-size:21px}
.cash small{display:block;font-size:9px;letter-spacing:.1em;color:var(--mut);text-transform:uppercase}

.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:12px}
.card h3{font-size:12px;letter-spacing:.1em;color:var(--rosa);margin-bottom:10px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.lbl{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--mut);display:block;margin-bottom:5px}
.fld{width:100%;background:var(--panel2);border:1px solid var(--line);color:var(--cream);border-radius:9px;
padding:9px 11px;font-size:16px;font-family:inherit}
.row{display:flex;gap:9px}.row>*{flex:1;min-width:0}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.btn{background:var(--rosa);color:#12181D;border:none;border-radius:10px;padding:12px 14px;font-weight:600;
font-size:14px;width:100%;font-family:inherit}
.btn.ghost{background:none;border:1px solid var(--line);color:var(--cream)}
.btn.mint{background:var(--mint)}.btn:disabled{opacity:.45}
.mini{border:1px solid var(--line);background:var(--panel2);color:var(--cream);border-radius:8px;padding:6px 9px;
font-size:12px;font-weight:600;font-family:inherit}
.mini.on{background:var(--rosa);color:#12181D;border-color:var(--rosa)}
.pill{display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;
padding:3px 7px;border-radius:6px;background:var(--panel2);color:var(--mut);border:1px solid var(--line)}
.pill.P{color:#F5B851;border-color:#4a3d22}.pill.D{color:#79C0FF;border-color:#22384a}
.pill.C{color:#57D9A3;border-color:#1f4437}.pill.A{color:#FF8FA0;border-color:#4a2530}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex:0 0 8px}
.t3{background:var(--mint)}.t2{background:var(--amber)}.t1{background:var(--red)}
.prow{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--line)}
.prow b{font-size:13.5px;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.prow small{font-size:11px;color:var(--mut)}
.prow.sold{opacity:.45}
.prow.selected{background:rgba(242,167,179,.10);border-radius:8px;padding-left:6px;padding-right:6px}
.qq{font-family:ui-monospace,Menlo,monospace;font-weight:700;font-size:14px}
.tick{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:13px;padding:7px 0;
border-bottom:1px solid var(--line)}.tick:last-child{border-bottom:none}
.bar{display:flex;height:24px;border-radius:8px;overflow:hidden;border:1px solid var(--line)}
.bar span{display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#0E141A;
font-family:ui-monospace,Menlo,monospace}
.bar2{display:flex;height:7px;margin-top:3px;border-radius:5px;overflow:hidden;border:1px solid var(--line)}
.block{background:linear-gradient(160deg,#1B2831,#131C24);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:12px}
.bname{font-family:'Archivo Black','Arial Black',Impact,sans-serif;font-size:22px;text-transform:uppercase;line-height:1.05}
.rail{position:relative;height:40px;margin:14px 0 4px;border-radius:8px;background:var(--panel);
border:1px solid var(--line);overflow:hidden}
.rail i{position:absolute;inset:0 auto 0 0;background:linear-gradient(90deg,#1f4437,#57D9A3);opacity:.28}
.rail b{position:absolute;top:0;bottom:0;width:2px;background:var(--rosa)}
.rail s{position:absolute;top:5px;font-size:9px;letter-spacing:.08em;color:var(--mut);text-decoration:none}
.bigno{font-family:ui-monospace,Menlo,monospace;font-weight:700;font-size:50px;line-height:1;letter-spacing:-.04em}
.trio{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;text-align:center;margin-top:10px}
.trio div{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px 4px}
.trio b{display:block;font-family:ui-monospace,Menlo,monospace;font-size:19px}
.trio small{font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:var(--mut)}
.note{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:9px 11px;font-size:12.5px;line-height:1.5;margin-top:8px}
.warn{background:#2a1f14;border:1px solid #4a3d22;color:#F5B851;border-radius:9px;padding:9px 11px;font-size:12.5px;line-height:1.5;margin-bottom:8px}
.warn.hi{background:#331a1a;border-color:#5a2a2a;color:#FF9E9E}
.agent{border-left:2px solid var(--rosa);padding:2px 0 2px 11px;margin:9px 0;font-size:14px;line-height:1.55}
.agent em{color:var(--rosa);font-style:normal;font-weight:600;font-size:11px;letter-spacing:.08em;
text-transform:uppercase;display:block;margin-bottom:3px}

/* campo */
.pitch{position:relative;background:linear-gradient(180deg,#16302a,#102420);border:1px solid #24483f;
border-radius:14px;padding:12px 10px;display:flex;flex-direction:column;justify-content:space-between;
min-height:430px;background-image:repeating-linear-gradient(180deg,rgba(255,255,255,.03) 0 40px,transparent 40px 80px)}
.prow2{display:flex;justify-content:space-evenly;gap:6px}
.slot{width:82px;height:62px;border:1px dashed #3d6b5e;border-radius:10px;background:rgba(0,0,0,.25);
display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:10px;color:#8fc3b3;
text-align:center;padding:3px;overflow:hidden}
.slot.full{border-style:solid;border-color:var(--mint);background:rgba(87,217,163,.14);color:var(--cream)}
.slot.hover{border-color:var(--rosa);background:rgba(242,167,179,.18)}
.slot b{font-size:11px;line-height:1.15;display:block;max-width:76px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.slot small{font-size:9px;color:var(--mut)}
.chip{display:inline-flex;align-items:center;gap:6px;background:var(--panel2);border:1px solid var(--line);
border-radius:9px;padding:6px 9px;font-size:12px;margin:0 6px 6px 0;touch-action:none}
.chip.sel{border-color:var(--rosa);background:rgba(242,167,179,.15)}
.ghost{position:fixed;z-index:99;pointer-events:none;opacity:.9;transform:translate(-50%,-50%)}
/* chat */
.chatWrap{display:flex;flex-direction:column;height:calc(100vh - 130px);height:calc(100dvh - 130px)}
.chatList{flex:1;overflow:auto;padding-right:4px}
.msg{max-width:78%;padding:10px 13px;border-radius:14px;margin-bottom:10px;font-size:14px;line-height:1.55;white-space:pre-wrap}
.msg.u{background:var(--rosa);color:#12181D;margin-left:auto;border-bottom-right-radius:4px}
.msg.a{background:var(--panel);border:1px solid var(--line);border-bottom-left-radius:4px}
.spin{display:inline-block;width:12px;height:12px;border:2px solid var(--line);border-top-color:var(--rosa);
border-radius:50%;animation:sp .7s linear infinite;vertical-align:middle}
@keyframes sp{to{transform:rotate(360deg)}}
.startBar{background:linear-gradient(90deg,rgba(242,167,179,.18),transparent);border:1px solid var(--rosa);
border-radius:12px;padding:12px 14px;margin-bottom:12px;font-size:13.5px;line-height:1.5}
.hide{display:none}
</style></head><body>
<div id="app">Carico…</div>
<script>
window.__boom=function(m,e){var a=document.getElementById("app");
 if(a)a.innerHTML='<div style="padding:20px;font-size:14px;line-height:1.6">'+
 '<b style="color:#F2A7B3">Errore nella pagina</b><br>'+m+(e?'<br><span style="color:#8CA0AF">'+e+'</span>':'')+
 '<br><br><span style="color:#8CA0AF">Riferisci questo messaggio.</span></div>';};
window.onerror=function(m,s,l,c){window.__boom(m,"riga "+l+":"+c);};
window.addEventListener("unhandledrejection",function(e){window.__boom("Promessa non gestita",e.reason&&(e.reason.message||e.reason));});
</script>
<script>
const R=["P","D","C","A"], RN={P:"Portieri",D:"Difensori",C:"Centrocampisti",A:"Attaccanti"};
const RC={P:"#F5B851",D:"#79C0FF",C:"#57D9A3",A:"#FF8FA0"};
const RO={P:"un portiere",D:"un difensore",C:"un centrocampista",A:"un attaccante"};
let S=null, tab="asta", cur=null, ev=null, scout=null, advice=null, alts=null, altsFor=null;
let q="", fr=null, lockPhase=true, busy="", sideOpen=false, chatBusy=false, selChip=null;
const $=s=>document.querySelector(s);
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

async function api(p,b){
  const r=await fetch(p,{method:b?"POST":"GET",headers:{"Content-Type":"application/json"},
    body:b?JSON.stringify(b):undefined});
  if(!r.ok) throw new Error("Il server ha risposto "+r.status+" su "+p);
  return r.json();
}
async function refresh(){
  try{ S=await api("/api/state"); if(!S.ready)tab="formato"; render(); }
  catch(e){ window.__boom("Non riesco a leggere i dati dal server.",(e&&e.message)||e); }
}
function go(k){ tab=k; sideOpen=false; render(); }

/* ---------------- LISTONE (colonna sinistra) ---------------- */
function listone(){
  if(!S.ready) return "";
  const phase=S.phase, active=(lockPhase?phase:fr);
  let a=S.players.slice();
  if(active) a=a.filter(p=>p.r===active);
  if(q.trim()){ const s=q.toLowerCase().trim();
    a=a.filter(p=>p.nome.toLowerCase().indexOf(s)>=0||p.team.toLowerCase().indexOf(s)>=0); }
  const liberi=a.filter(p=>p.buyer===undefined), presi=a.filter(p=>p.buyer!==undefined);
  const rows=liberi.concat(presi).slice(0,300);
  let h='<div class="sHead">'+
   '<div style="display:flex;align-items:center;gap:8px;margin-bottom:9px">'+
   '<span class="pill '+phase+'" style="padding:5px 9px">FASE: '+RN[phase].toUpperCase()+'</span>'+
   '<button class="mini'+(lockPhase?' on':'')+'" onclick="lockPhase=!lockPhase;fr=null;render()">'+
   (lockPhase?'filtrato':'sbloccato')+'</button>'+
   '<button class="mini sideToggle" style="margin-left:auto" onclick="sideOpen=false;render()">chiudi</button></div>'+
   '<input class="fld" id="srch" placeholder="Cerca giocatore o squadra" value="'+esc(q)+'" '+
   'oninput="q=this.value;renderList()">';
  if(!lockPhase){
    h+='<div style="display:flex;gap:5px;margin-top:8px">'+
    ['tutti'].concat(R).map(r=>'<button class="mini'+((r==='tutti'&&!fr)||fr===r?' on':'')+'" style="flex:1" '+
     'onclick="fr='+(r==='tutti'?'null':"'"+r+"'")+';render()">'+(r==='tutti'?'Tutti':r)+'</button>').join("")+'</div>';
  }
  h+='<div style="font-size:11px;color:var(--mut);margin-top:8px">'+liberi.length+' liberi · '+presi.length+' assegnati</div>';
  h+='</div><div class="sList" id="sList">'+rowsHTML(rows)+'</div>';
  return h;
}
function rowsHTML(rows){
  return rows.map(p=>{
    const sold=p.buyer!==undefined;
    const right = sold
      ? '<div style="text-align:right;width:74px"><div class="qq" style="color:var(--mut)">'+p.paid+'</div>'+
        '<small style="font-size:9.5px;color:var(--mut);display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(p.buyer_name)+'</small></div>'
      : '<div style="text-align:right;width:74px"><div class="qq">'+p.base+'</div>'+
        '<small style="font-size:10px;color:var(--mut)">max '+p.max+'</small></div>';
    return '<div class="prow'+(sold?' sold':'')+(cur&&cur.id===p.id?' selected':'')+'" onclick="pick(\''+p.id+'\')">'+
      '<span class="pill '+p.r+'" style="width:24px">'+p.r+'</span>'+
      '<span class="dot t'+p.t+'"></span>'+
      '<div style="flex:1;min-width:0"><b>'+esc(p.nome)+'</b><small>'+esc(p.team)+
      (p.stars?' · '+"★".repeat(p.stars):'')+'</small></div>'+right+'</div>';
  }).join("");
}
function renderList(){ const el=$("#sList"); if(el) el.innerHTML=rowsHTML(filtered()); }
function filtered(){
  const active=(lockPhase?S.phase:fr);
  let a=S.players.slice();
  if(active) a=a.filter(p=>p.r===active);
  if(q.trim()){ const s=q.toLowerCase().trim();
    a=a.filter(p=>p.nome.toLowerCase().indexOf(s)>=0||p.team.toLowerCase().indexOf(s)>=0); }
  return a.filter(p=>p.buyer===undefined).concat(a.filter(p=>p.buyer!==undefined)).slice(0,300);
}

/* ---------------- ASTA ---------------- */
async function pick(id){
  const p=S.players.find(x=>x.id===id);
  if(p && p.buyer!==undefined){ if(confirm("Annullare l'acquisto di "+p.nome+"?")) return undo(id); return; }
  const r=await api("/api/eval",{id:id}); cur=r.player; ev=r.ev; scout=null;
  tab="asta"; sideOpen=false; render();
}
async function undo(id){ await api("/api/undo",{id:id}); if(cur&&cur.id===id){cur=null;ev=null;} await refresh(); }
async function assignCur(){
  const who=+$("#a_who").value, pid=cur.id;
  await api("/api/assign",{id:pid,buyer:who,price:+$("#a_price").value});
  cur=null;ev=null;scout=null;
  if(who===0){ try{const r=await api("/api/alternatives",{id:pid,n:5}); alts=r.alts; altsFor=r.bought;}catch(e){alts=null;} }
  await refresh();
}
async function star(id,e){ if(e)e.stopPropagation(); await api("/api/target",{id:id}); await refresh(); }

function viewAsta(){
  let h="";
  if(cur&&ev){ const p=cur;
    h+='<div class="block"><div style="display:flex;justify-content:space-between;gap:10px">'+
    '<div><div class="bname">'+esc(p.nome)+'</div>'+
    '<div style="font-size:12.5px;color:var(--mut);margin-top:3px">'+esc(p.team)+
    ' · quotazione '+p.q+' · fantavalore '+(p.fvm||'-')+'</div>'+
    '<div style="font-size:12px;margin-top:5px;color:'+(ev.tit===3?'var(--mint)':ev.tit===2?'var(--amber)':'var(--red)')+'">● '+ev.tit_label+'</div></div>'+
    '<div style="text-align:right"><span class="pill '+p.r+'">'+p.r+'</span><br>'+
    '<button class="mini" style="margin-top:8px" onclick="star(\''+p.id+'\')">'+(ev.stars?"★".repeat(ev.stars):"☆ obiettivo")+'</button></div></div>'+
    '<div class="rail"><i style="width:'+Math.max(4,Math.min(100,ev.max/Math.max(ev.max,S.parts[0].credits)*100))+'%"></i>'+
    '<b style="left:'+Math.max(0,Math.min(99,ev.base/Math.max(ev.max,1)*100))+'%"></b>'+
    '<s style="left:9px">AFFARE</s><s style="right:9px">ROTTURA</s></div>'+
    '<div style="text-align:center"><div class="lbl" style="margin-bottom:0">Non superare</div>'+
    '<div class="bigno" style="color:'+(ev.max<=ev.base?'var(--amber)':'var(--mint)')+'">'+ev.max+'</div></div>'+
    '<div class="trio"><div><b style="color:var(--mint)">'+ev.min+'</b><small>affare sotto</small></div>'+
    '<div><b>'+ev.base+'</b><small>prezzo reale</small></div>'+
    '<div><b style="color:var(--rosa)">'+ev.hard_cap+'</b><small>tetto fisico</small></div></div>'+
    '<div class="note">'+(ev.rivals_count===0
      ? 'Nessun avversario ha ancora bisogno di questo ruolo. <b style="color:var(--mint)">Aprilo a 1 credito.</b>'
      : 'Il rivale più pericoloso è <b>'+esc(ev.top_rival_name)+'</b>, che può arrivare a <b class="mono" style="color:var(--rosa)">'+
        ev.top_rival+'</b>. '+ev.contenders+(ev.contenders===1?' squadra può':' squadre possono')+' permetterselo al prezzo reale. '+
        (ev.max>=ev.beat?'Con <b class="mono" style="color:var(--mint)">'+ev.beat+'</b> lo chiudi comunque.'
                        :'Oltre '+ev.max+' non ti conviene seguirlo.'))+'</div>'+
    '<div class="row" style="margin-top:12px">'+
    '<button class="mini" onclick="askScout(false)"'+(busy?' disabled':'')+'>'+(busy==='scout'?'<span class="spin"></span>':'Valuta')+'</button>'+
    '<button class="mini" onclick="askScout(true)"'+(busy?' disabled':'')+'>+ notizie</button>'+
    '<button class="mini" onclick="cur=null;render()">Chiudi</button></div>';
    if(scout&&scout.player===p.id){
      h+='<div style="margin-top:12px;border-top:1px solid var(--line);padding-top:11px">';
      if(scout.errore) h+='<div class="warn">'+esc(scout.errore)+'</div>';
      else h+='<div class="agent"><em>Agente valutazioni</em>'+esc(scout.giudizio)+'</div>'+
        '<div class="trio"><div><b>'+esc(scout.valore_equo)+'</b><small>valore equo</small></div>'+
        '<div><b>'+esc(scout.prezzo_massimo)+'</b><small>max agente</small></div>'+
        '<div><b style="font-size:12px;line-height:19px">'+esc(scout.fantamedia_attesa)+'</b><small>fm attesa</small></div></div>'+
        '<div style="font-size:12.5px;margin-top:10px;line-height:1.55">'+
        (scout.punti_forza||[]).map(s=>'<div><span class="dot t3"></span> '+esc(s)+'</div>').join("")+
        (scout.rischi||[]).map(s=>'<div><span class="dot t1"></span> '+esc(s)+'</div>').join("")+'</div>'+
        '<div style="margin-top:9px;font-family:\'Archivo Black\',sans-serif;text-transform:uppercase;font-size:14px;color:'+
        (/lasciare/i.test(scout.verdetto||"")?'var(--red)':'var(--mint)')+'">'+esc(scout.verdetto)+'</div>';
      h+='</div>';
    }
    h+='<div style="margin-top:12px;border-top:1px solid var(--line);padding-top:11px">'+
    '<span class="lbl">Aggiudicato a</span><div class="row" style="margin-bottom:8px">'+
    '<select class="fld" id="a_who">'+S.parts.map((x,i)=>'<option value="'+i+'">'+(i===0?'► ':'')+esc(x.name)+'</option>').join("")+'</select>'+
    '<input class="fld mono" id="a_price" style="max-width:100px;text-align:center" type="number" min="1" value="'+ev.max+'"></div>'+
    '<button class="btn mint" onclick="assignCur()">Aggiudica</button></div></div>';
  } else {
    h+='<div class="card" style="text-align:center;padding:26px 14px;color:var(--mut);font-size:14px">'+
    'Tocca un giocatore nel listone per portarlo sul banco.<br>Il prezzo di rottura si calcola sul momento.</div>';
  }
  if(alts&&alts.length&&!cur) h+=altsHTML();
  h+='<div class="card"><h3>Ultimi aggiudicati</h3>'+storicoHTML(10)+'</div>';
  return h;
}
function altsHTML(){
  return '<div class="card" style="border-color:var(--rosa)">'+
  '<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px">'+
  '<h3 style="margin:0">E adesso</h3><button class="mini" onclick="alts=null;render()">chiudi</button></div>'+
  '<div style="font-size:12px;color:var(--mut);line-height:1.5;margin-bottom:8px">Preso '+esc(altsFor?altsFor.nome:"")+
  '. In ordine di priorità, i prossimi cinque nomi su cui muoverti.</div>'+
  alts.map((a,i)=>'<div class="prow" onclick="pick(\''+a.id+'\')">'+
    '<span class="mono" style="width:16px;color:var(--rosa);font-weight:700">'+(i+1)+'</span>'+
    '<span class="pill '+a.r+'" style="width:24px">'+a.r+'</span>'+
    '<span class="dot t'+a.tit_n+'"></span>'+
    '<div style="flex:1;min-width:0"><b>'+esc(a.nome)+'</b><small>'+esc(a.team)+' · '+esc(a.why)+'</small></div>'+
    '<div style="text-align:right;width:66px"><div class="qq">'+a.base+'</div>'+
    '<small style="font-size:10px;color:var(--mut)">max '+a.max+'</small></div></div>').join("")+'</div>';
}
function storicoHTML(n){
  const sold=S.players.filter(p=>p.buyer!==undefined).slice(-n).reverse();
  if(!sold.length) return '<div style="font-size:12.5px;color:var(--mut)">L\'asta non è ancora partita.</div>';
  return sold.map(p=>'<div class="tick"><span class="pill '+p.r+'" style="width:24px">'+p.r+'</span>'+
   '<span style="flex:1">'+esc(p.nome)+' <small style="color:var(--mut)">'+esc(p.team)+'</small></span>'+
   '<span style="font-size:11.5px;color:var(--mut)">'+esc(p.buyer_name)+'</span>'+
   '<span class="mono">'+p.paid+'</span>'+
   '<button class="mini" style="padding:3px 7px" onclick="undo(\''+p.id+'\')">↺</button></div>').join("");
}

/* ---------------- SQUADRE ---------------- */
function viewSquadre(){
  let h='<div class="grid2">';
  S.parts.forEach((pt,i)=>{
    const cap=S.caps[i], rose=S.rose[String(i)]||[], pg=S.pagelle[i];
    h+='<div class="card" style="border-color:'+(i===0?'var(--rosa)':'var(--line)')+'">'+
    '<div style="display:flex;justify-content:space-between;align-items:baseline">'+
    '<b style="font-size:15px;color:'+(i===0?'var(--rosa)':'var(--cream)')+'">'+esc(pt.name)+'</b>'+
    '<span class="mono" style="font-size:22px;font-weight:700">'+pt.credits+'</span></div>'+
    '<div style="font-size:11px;color:var(--mut);margin-bottom:8px">spesi '+(S.cfg.budget-pt.credits)+
    ' · max su un nome '+cap.cap+' · '+cap.medio+' per slot</div>'+
    '<div style="display:flex;gap:6px;margin-bottom:8px">'+
    R.map(r=>{const d=pt.filled[r]||0,full=d>=S.cfg.slots[r];
      return '<div style="flex:1;text-align:center;background:var(--panel2);border:1px solid '+(full?RC[r]:'var(--line)')+
      ';border-radius:8px;padding:5px 2px"><div class="mono" style="font-size:13px;color:'+(full?RC[r]:'var(--cream)')+'">'+
      d+'/'+S.cfg.slots[r]+'</div><div style="font-size:9px;color:var(--mut)">'+r+'</div></div>';}).join("")+'</div>';
    if(pg&&pg.indice) h+='<div class="note" style="margin-top:0;margin-bottom:8px">Pagella d\'asta: <b class="mono" style="color:'+
      (pg.indice>=1.12?'var(--mint)':pg.indice<=0.88?'var(--red)':'var(--cream)')+'">'+pg.indice.toFixed(2)+'</b> — '+pg.giudizio+
      ' <span style="color:var(--mut)">(valore preso ~'+pg.valore+' contro '+pg.speso+' spesi)</span></div>';
    if(rose.length) h+=rose.map(p=>'<div class="tick"><span class="pill '+p.r+'" style="width:24px">'+p.r+'</span>'+
      '<span class="dot t'+p.t+'"></span>'+
      '<span style="flex:1">'+esc(p.nome)+' <small style="color:var(--mut)">'+esc(p.team)+'</small></span>'+
      '<span class="mono">'+p.price+'</span>'+
      '<button class="mini" style="padding:3px 7px" onclick="undo(\''+p.id+'\')">↺</button></div>').join("");
    else h+='<div style="font-size:12.5px;color:var(--mut)">Nessun giocatore.</div>';
    h+='</div>';
  });
  return h+'</div>';
}

/* ---------------- LA MIA SQUADRA ---------------- */
function slotKeys(){
  const m=S.moduli[S.formation.modulo]||{D:3,C:4,A:3};
  const out=[["P",1]];
  R.slice(1).forEach(r=>out.push([r,m[r]]));
  return out;
}
function viewMia(){
  const rose=S.rose["0"]||[], f=S.formation, placed=f.slots||{};
  const byId={}; rose.forEach(p=>byId[p.id]=p);
  const usati=new Set(Object.values(placed));
  const panca=rose.filter(p=>!usati.has(p.id));
  let h='<div class="grid2">';
  // campo
  h+='<div class="card"><h3>Formazione</h3>'+
  '<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">'+
  Object.keys(S.moduli).map(m=>'<button class="mini'+(f.modulo===m?' on':'')+'" onclick="setModulo(\''+m+'\')">'+m+'</button>').join("")+
  '</div><div class="pitch" id="pitch">';
  slotKeys().slice().reverse().forEach(([r,n])=>{
    h+='<div class="prow2">';
    for(let i=1;i<=n;i++){
      const k=r+i, pid=placed[k], p=pid?byId[pid]:null;
      h+='<div class="slot'+(p?' full':'')+'" data-slot="'+k+'" onclick="tapSlot(\''+k+'\')">'+
        (p?'<span class="dot t'+p.t+'"></span><b>'+esc(p.nome)+'</b><small>'+esc(p.team)+' · '+p.price+'</small>'
          :'<span style="opacity:.7">'+r+'</span>')+'</div>';
    }
    h+='</div>';
  });
  h+='</div><div style="font-size:11.5px;color:var(--mut);margin-top:8px">'+
  'Trascina un giocatore dalla panchina al ruolo, oppure toccalo e poi tocca la casella. Tocca una casella piena per liberarla.</div></div>';
  // panchina + numeri
  h+='<div><div class="card"><h3>In rosa, fuori dal campo</h3><div id="bench">'+
  (rose.length===0?'<div style="font-size:12.5px;color:var(--mut)">Non hai ancora nessun giocatore in rosa.</div>'
   :panca.length?panca.map(p=>'<span class="chip'+(selChip===p.id?' sel':'')+'" data-pid="'+p.id+'" onclick="tapChip(\''+p.id+'\')">'+
    '<span class="pill '+p.r+'" style="width:22px">'+p.r+'</span><span class="dot t'+p.t+'"></span>'+esc(p.nome)+
    '<span class="mono" style="color:var(--mut)">'+p.price+'</span></span>').join("")
   :'<div style="font-size:12.5px;color:var(--mut)">Tutti schierati.</div>')+'</div></div>';
  h+='<div class="card"><h3>I miei numeri</h3>'+allocBar(S.alloc,S.cfg.budget,S.parts[0].spent)+
   '<div style="margin-top:10px">'+R.map(r=>{
     const n=S.parts[0].filled[r]||0;
     return '<div class="tick"><span class="pill '+r+'">'+r+'</span>'+
     '<span style="flex:1;font-size:12.5px;color:var(--mut)">'+n+'/'+S.cfg.slots[r]+' presi</span>'+
     '<span class="mono">'+S.role_spent[r]+' / '+S.role_budget[r]+'</span></div>';}).join("")+'</div>'+
   '<div style="display:flex;justify-content:space-between;font-size:12px;color:var(--mut);margin-top:10px">'+
   '<span>Crediti <b class="mono" style="color:var(--cream)">'+S.parts[0].credits+'</b></span>'+
   '<span>Slot liberi <b class="mono" style="color:var(--cream)">'+S.my_slots_left+'</b></span>'+
   '<span>Scostamento <b class="mono" style="color:'+(S.flex>=0?'var(--mint)':'var(--amber)')+'">'+
   (S.flex>=0?'+':'')+S.flex+'</b></span></div></div></div>';
  return h+'</div>';
}
async function setModulo(m){
  S.formation.modulo=m; S.formation.slots={};
  await api("/api/formation",S.formation); await refresh();
}
async function place(pid,k){
  const f=S.formation;
  const r=k[0]; const p=(S.rose["0"]||[]).find(x=>x.id===pid);
  if(!p) return;
  if(p.r!==r){ alert(p.nome+" è "+RO[p.r]+": non può occupare quella casella."); return; }
  for(const kk in f.slots) if(f.slots[kk]===pid) delete f.slots[kk];
  f.slots[k]=pid; selChip=null;
  await api("/api/formation",f); await refresh();
}
async function clearSlot(k){
  delete S.formation.slots[k]; await api("/api/formation",S.formation); await refresh();
}
function tapChip(pid){ selChip=(selChip===pid?null:pid); render(); }
function tapSlot(k){
  if(selChip){ place(selChip,k); return; }
  if(S.formation.slots&&S.formation.slots[k]) clearSlot(k);
}
/* trascinamento con pointer events: funziona anche col dito su iPad */
function initDrag(){
  const bench=document.getElementById("bench"); if(!bench) return;
  bench.querySelectorAll(".chip").forEach(ch=>{
    ch.addEventListener("pointerdown",e=>{
      const pid=ch.dataset.pid; let ghost=null, moved=false;
      const move=ev2=>{
        if(!moved && Math.abs(ev2.clientY-e.clientY)+Math.abs(ev2.clientX-e.clientX)<6) return;
        moved=true;
        if(!ghost){ ghost=ch.cloneNode(true); ghost.className="chip ghost"; document.body.appendChild(ghost); }
        ghost.style.left=ev2.clientX+"px"; ghost.style.top=ev2.clientY+"px";
        document.querySelectorAll(".slot.hover").forEach(s=>s.classList.remove("hover"));
        const t=document.elementFromPoint(ev2.clientX,ev2.clientY);
        const sl=t&&t.closest?t.closest(".slot"):null; if(sl) sl.classList.add("hover");
      };
      const up=ev2=>{
        document.removeEventListener("pointermove",move);
        document.removeEventListener("pointerup",up);
        if(ghost) ghost.remove();
        document.querySelectorAll(".slot.hover").forEach(s=>s.classList.remove("hover"));
        if(!moved) return;
        const t=document.elementFromPoint(ev2.clientX,ev2.clientY);
        const sl=t&&t.closest?t.closest(".slot"):null;
        if(sl) place(pid,sl.dataset.slot);
      };
      document.addEventListener("pointermove",move);
      document.addEventListener("pointerup",up);
    });
  });
}

/* ---------------- STRATEGIA ---------------- */
function viewStrategia(){
  let h="";
  if(S.alerts&&S.alerts.length) h+=S.alerts.map(a=>'<div class="warn'+(a.lvl==='alto'?' hi':'')+'">'+esc(a.txt)+'</div>').join("");
  h+='<div class="grid2"><div>';
  h+='<div class="card"><h3>Agente stratega</h3>'+
  '<div style="font-size:13px;color:var(--mut);line-height:1.5;margin-bottom:10px">Legge crediti, slot, fase, inflazione e casse avversarie, poi riscrive la ripartizione del budget.</div>'+
  '<button class="btn" onclick="askStrat()"'+(busy?' disabled':'')+'>'+
  (busy==='strat'?'<span class="spin"></span> sta leggendo l\'asta…':'Ricalcola la strategia')+'</button>';
  if(advice){
    if(advice.errore) h+='<div class="warn" style="margin-top:12px">'+esc(advice.errore)+'</div>';
    else{ h+='<div style="margin-top:14px">';
      if(advice.fase) h+='<span class="pill">fase '+esc(advice.fase)+'</span>';
      h+='<div class="agent"><em>Lettura</em>'+esc(advice.lettura)+'</div>';
      if(advice.perche_alloc) h+='<div class="agent"><em>Nuova ripartizione</em>'+esc(advice.perche_alloc)+'</div>';
      if((advice.mosse||[]).length) h+='<div class="agent"><em>Mosse ora</em>'+
        advice.mosse.map(m=>'<div style="margin-bottom:5px">— '+esc(m)+'</div>').join("")+'</div>';
      if(advice.rischio) h+='<div class="warn" style="margin-top:8px"><b>Rischio:</b> '+esc(advice.rischio)+'</div>';
      h+='</div>'; }
  }
  h+='</div>';
  h+='<div class="card"><h3>Ripartizione attiva</h3>'+allocBar(S.alloc,S.cfg.budget,S.parts[0].spent)+
  '<div style="margin-top:10px">'+R.map(r=>'<div class="tick"><span class="pill '+r+'">'+r+'</span>'+
   '<span style="flex:1;font-size:12.5px;color:var(--mut)">'+(S.parts[0].filled[r]||0)+'/'+S.cfg.slots[r]+' presi</span>'+
   '<span class="mono">'+S.role_spent[r]+' / '+S.role_budget[r]+'</span></div>').join("")+'</div></div>';
  h+='</div><div>';
  h+=(alts&&alts.length)?altsHTML():'<div class="card"><h3>Prossimi acquisti</h3>'+
   '<div style="font-size:12.5px;color:var(--mut);line-height:1.5">Appena aggiudichi un giocatore, qui compaiono le cinque alternative migliori: il vice della stessa squadra, gli equivalenti per rendimento e prezzo, il tuo reparto più scoperto.</div></div>';
  h+='<div class="card"><h3>Casse avversarie</h3>'+S.caps.map((c,i)=>'<div class="tick">'+
   '<span style="font-weight:'+(i===0?700:400)+';color:'+(i===0?'var(--rosa)':'var(--cream)')+';flex:1">'+esc(c.name)+'</span>'+
   '<span class="mono" style="font-size:11px;color:var(--mut)">'+R.map(r=>c.filled[r]||0).join("·")+'</span>'+
   '<span class="mono" style="font-weight:600">'+c.credits+'</span></div>').join("")+
   '<div style="font-size:11.5px;color:var(--mut);margin-top:8px">Inflazione mercato <b class="mono" style="color:var(--cream)">×'+
   S.inflation+'</b> · massimo che un avversario può offrire su un nome <b class="mono" style="color:var(--cream)">'+
   Math.max.apply(null,S.caps.slice(1).map(c=>c.cap))+'</b></div></div>';
  h+='<div class="card"><h3>Pagelle d\'asta</h3>'+
   '<div style="font-size:12px;color:var(--mut);margin-bottom:8px">Valore di mercato acquistato per credito speso. Sopra 1,12 sta facendo affari; sotto 0,88 sta pagando troppo.</div>'+
   S.pagelle.filter(p=>p.indice).sort((a,b)=>b.indice-a.indice).map(p=>'<div class="tick">'+
   '<span style="flex:1;color:'+(p.i===0?'var(--rosa)':'var(--cream)')+'">'+esc(p.name)+'</span>'+
   '<span style="font-size:11.5px;color:var(--mut)">'+p.giocatori+' gioc. · '+p.speso+' cr</span>'+
   '<span class="mono" style="font-weight:700;color:'+(p.indice>=1.12?'var(--mint)':p.indice<=0.88?'var(--red)':'var(--cream)')+'">'+
   p.indice.toFixed(2)+'</span></div>').join("")||'<div style="font-size:12.5px;color:var(--mut)">Ancora nessun acquisto.</div>';
  h+='</div></div></div>';
  return h;
}
async function askStrat(){ busy="strat"; render();
  try{ advice=await api("/api/agent",{kind:"strategist"}); }catch(e){ advice={errore:e.message}; }
  busy=""; await refresh(); }
async function askScout(news){ busy="scout"; render();
  try{ scout=await api("/api/agent",{kind:"scout",id:cur.id,news:!!news}); }catch(e){ scout={errore:e.message,player:cur.id}; }
  busy=""; render(); }

/* ---------------- CHAT ---------------- */
function viewChat(){
  const msgs=S.chat||[];
  let h='<div class="chatWrap"><div class="chatList" id="chatList">';
  if(!S.has_key) h+='<div class="warn hi">La chat e gli agenti richiedono una chiave API Anthropic: '+
   'incollala in <b>Formato → Agenti e chat</b>. Senza chiave il resto dell\'app funziona lo stesso.</div>';
  if(!msgs.length) h+='<div class="card"><h3>Consulente d\'asta</h3>'+
   '<div style="font-size:13.5px;line-height:1.6;color:var(--mut)">Vede lo stato dell\'asta in tempo reale: crediti, rose, casse avversarie, fase. Chiedigli cose come:<br><br>'+
   '"Conviene puntare tutto su un attaccante da 150 o prenderne due da 70?"<br>'+
   '"Chi mi consigli come terzo portiere sotto i 5 crediti?"<br>'+
   '"Squadra 4 ha 300 crediti e solo gli attaccanti scoperti, come mi comporto?"</div></div>';
  h+=msgs.map(m=>'<div class="msg '+(m.role==='user'?'u':'a')+'"'+
   (m.err?' style="border-color:#5a2a2a;color:#FF9E9E"':'')+'>'+esc(m.content)+'</div>').join("");
  if(chatBusy) h+='<div class="msg a"><span class="spin"></span> sto guardando l\'asta…</div>';
  h+='</div><div class="row" style="margin-top:10px">'+
  '<textarea class="fld" id="chatIn" rows="2" placeholder="Chiedi qualcosa sull\'asta…" '+
  'onkeydown="if(event.key===\'Enter\'&&!event.shiftKey){event.preventDefault();sendChat()}"></textarea>'+
  '<button class="btn" style="max-width:110px" onclick="sendChat()"'+(chatBusy?' disabled':'')+'>Invia</button></div></div>';
  return h;
}
async function sendChat(){
  const el=$("#chatIn"); if(!el) return;
  const t=el.value.trim(); if(!t||chatBusy) return;
  el.value=""; chatBusy=true;
  S.chat=(S.chat||[]).concat([{role:"user",content:t}]); render();
  let err=null;
  try{ const r=await api("/api/chat",{msg:t}); if(r&&r.errore) err=r.errore; }
  catch(e){ err=(e&&e.message)||String(e); }
  chatBusy=false; await refresh();
  if(err){ const cl=$("#chatList");
    if(cl) cl.insertAdjacentHTML("beforeend",
      '<div class="msg a" style="border-color:#5a2a2a;color:#FF9E9E">Non riesco a rispondere: '+esc(err)+'</div>'); }
  const cl=$("#chatList"); if(cl) cl.scrollTop=cl.scrollHeight;
}

/* ---------------- FORMATO ---------------- */
function allocBar(alloc,budget,spent){
  let h='<div class="bar">'+R.map(r=>'<span style="width:'+alloc[r]+'%;background:'+RC[r]+';opacity:.85">'+
    (alloc[r]>=8?Math.round(alloc[r]/100*budget):"")+'</span>').join("")+'</div>';
  if(spent){ h+='<div class="bar2">'+R.map(r=>{
    const cap=alloc[r]/100*budget||1,p=Math.min(1,(spent[r]||0)/cap);
    return '<span style="width:'+alloc[r]+'%;background:var(--panel2);position:relative">'+
     '<i style="position:absolute;inset:0 auto 0 0;width:'+(p*100)+'%;background:'+((spent[r]||0)>cap?'var(--red)':RC[r])+'"></i></span>';
   }).join("")+'</div>'; }
  return h;
}
function viewFormato(){
  const c=S.cfg,a=S.alloc;
  let h='';
  if(!S.ready) h+='<button class="btn" style="margin-bottom:12px" onclick="startAuction()">Apri l\'asta</button>';
  h+='<div class="grid2"><div><div class="card"><h3>Formato della lega</h3>'+
  '<div class="row" style="margin-bottom:10px">'+
  '<div><span class="lbl">Partecipanti</span><input class="fld mono" id="f_teams" type="number" min="4" max="16" value="'+c.teams+'" onchange="readCfg();render()"></div>'+
  '<div><span class="lbl">Crediti</span><input class="fld mono" id="f_budget" type="number" min="100" step="50" value="'+c.budget+'"></div></div>'+
  '<span class="lbl">Slot di rosa</span><div class="grid4">'+
  R.map(r=>'<div><input class="fld mono" style="text-align:center" id="f_s'+r+'" type="number" min="1" value="'+c.slots[r]+'">'+
   '<div style="text-align:center;font-size:10px;color:var(--mut);margin-top:4px">'+r+'</div></div>').join("")+'</div>'+
  '<label style="display:flex;gap:9px;align-items:center;margin-top:12px;font-size:14px">'+
  '<input type="checkbox" id="f_mod"'+(c.mod_difesa?' checked':'')+'> Modificatore di difesa attivo</label></div>'+
  '<div class="card"><h3>Chi c\'è in lega</h3>';
  for(let i=0;i<c.teams;i++) h+='<div style="display:flex;gap:8px;align-items:center;margin-bottom:6px">'+
   '<span class="mono" style="width:20px;font-size:12px;color:'+(i===0?'var(--rosa)':'var(--mut)')+'">'+(i+1)+'</span>'+
   '<input class="fld nm" style="padding:7px 10px;font-size:14px" placeholder="'+(i===0?'La mia squadra':'Squadra '+(i+1))+
   '" value="'+esc((c.names&&c.names[i])||"")+'"></div>';
  h+='</div></div><div>';
  h+='<div class="card"><h3>Strategia di partenza</h3>';
  Object.keys(S.presets).forEach(k=>{const p=S.presets[k];
    h+='<button onclick="setPreset(\''+k+'\')" style="display:block;width:100%;text-align:left;margin-bottom:8px;padding:10px 12px;'+
    'border-radius:11px;background:'+(S.preset===k?'rgba(242,167,179,.12)':'var(--panel2)')+';border:1px solid '+
    (S.preset===k?'var(--rosa)':'var(--line)')+';color:var(--cream);font-family:inherit">'+
    '<div style="display:flex;justify-content:space-between"><b style="font-size:14px">'+p.label+'</b>'+
    '<span class="mono" style="font-size:11px;color:var(--mut)">'+R.map(r=>p.alloc[r]).join("·")+'</span></div>'+
    '<small style="color:var(--mut);font-size:12px">'+p.note+'</small></button>';});
  h+=allocBar(a,c.budget)+'<div style="margin-top:10px">'+R.map(r=>
   '<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px"><span class="pill '+r+'" style="width:38px">'+r+'</span>'+
   '<input type="range" min="3" max="70" value="'+a[r]+'" style="flex:1;accent-color:'+RC[r]+'" oninput="slide(\''+r+'\',this.value)">'+
   '<span class="mono" style="width:60px;text-align:right;font-size:13px" id="al_'+r+'">'+Math.round(a[r]/100*c.budget)+'cr</span></div>').join("")+'</div></div>';
  h+='<div class="card"><h3>Listone</h3>'+
  '<div class="note" style="margin-top:0">In uso: <b>'+S.n_players+' giocatori</b>'+
  (S.n_players>500?' — listone ufficiale Fantacalcio.it 2026/27':'')+'. Puoi sostituirlo incollando quello della tua lega.</div>'+
  '<div style="margin-top:10px"><span class="lbl">Incolla (R;Nome;Squadra;Qt;…;FVM)</span>'+
  '<textarea class="fld" id="imp" rows="3"></textarea>'+
  '<button class="btn ghost" style="margin-top:8px" onclick="doImport()">Importa listone</button>'+
  '<div id="impmsg" style="font-size:12px;color:var(--mut);margin-top:7px"></div></div></div>';
  h+='<div class="card"><h3>Agenti e chat</h3>'+
  '<div style="font-size:12.5px;color:var(--mut);line-height:1.5;margin-bottom:9px">Asta, prezzi e formazione funzionano offline. Gli agenti e la chat richiedono una chiave API Anthropic, che resta su questo dispositivo.</div>'+
  '<input class="fld" id="apikey" type="password" placeholder="'+(S.has_key?'chiave salvata — sostituiscila se vuoi':'sk-ant-...')+'">'+
  '<button class="btn ghost" style="margin-top:8px" onclick="saveKey()">Salva chiave</button></div>';
  h+='<button class="btn" onclick="startAuction()">'+(S.ready?"Ricomincia l'asta con questo formato":"Apri l'asta")+'</button>';
  h+='</div></div>';
  return h;
}
function slide(r,v){ v=+v;
  const o=R.filter(x=>x!==r), s=o.reduce((a,x)=>a+S.alloc[x],0)||1, rest=100-v;
  S.alloc[r]=v; o.forEach(x=>S.alloc[x]=Math.round(S.alloc[x]/s*rest)); S.preset="custom";
  R.forEach(x=>{const el=document.getElementById("al_"+x); if(el)el.textContent=Math.round(S.alloc[x]/100*S.cfg.budget)+"cr";});
  saveCfg();
}
function setPreset(k){ S.preset=k; S.alloc=Object.assign({},S.presets[k].alloc); saveCfg(); render(); }
function readCfg(){
  if(!$("#f_teams")) return;
  S.cfg.teams=Math.max(4,Math.min(16,parseInt($("#f_teams").value)||10));
  S.cfg.budget=parseInt($("#f_budget").value)||500;
  R.forEach(r=>S.cfg.slots[r]=parseInt(document.getElementById("f_s"+r).value)||1);
  S.cfg.mod_difesa=$("#f_mod").checked;
  S.cfg.names=[].slice.call(document.querySelectorAll(".nm")).map(e=>e.value);
}
async function saveCfg(){ readCfg(); await api("/api/config",{cfg:S.cfg,alloc:S.alloc,preset:S.preset}); }
async function startAuction(){ await saveCfg(); await api("/api/start",{}); tab="asta"; alts=null; await refresh(); }
async function saveKey(){ const k=$("#apikey").value.trim(); if(!k)return;
  await api("/api/key",{key:k}); $("#apikey").value=""; S.has_key=true; alert("Chiave salvata su questo dispositivo."); }
async function doImport(){ const r=await api("/api/import",{text:$("#imp").value});
  $("#impmsg").textContent=r.n?r.n+" giocatori caricati.":"Non ho riconosciuto le colonne. Servono ruolo, nome, squadra e quotazione.";
  if(r.n) await refresh(); }

/* ---------------- RENDER ---------------- */
function render(){
  if(!S){ return; }
  if(!S.ready) tab="formato";
  const navAll=[["asta","Asta"],["squadre","Squadre"],["mia","La mia squadra"],["strategia","Strategia"],["chat","Chat"],["formato","Formato"]];
  const nav = S.ready ? navAll : [["formato","Formato"]];
  const body = tab==="squadre"?viewSquadre() : tab==="mia"?viewMia() : tab==="strategia"?viewStrategia() :
               tab==="chat"?viewChat() : tab==="formato"?viewFormato() : viewAsta();
  const start = S.ready ? '' :
   '<div class="startBar"><b>Prima di cominciare:</b> controlla il formato della lega e i nomi dei partecipanti, '+
   'poi premi <b>Apri l\'asta</b> in fondo alla pagina. Da quel momento compare il listone a sinistra e il resto del menu.</div>';
  $("#app").innerHTML =
   '<div class="shell'+(S.ready?'':' solo')+'">'+
   (S.ready?'<aside class="side'+(sideOpen?' open':'')+'">'+listone()+'</aside>':'')+
   '<div class="main"><div class="topbar">'+
   '<div class="brand"><h1>Banco d\'asta</h1><span>v'+S.version+'</span></div>'+
   (S.ready?'<button class="mini sideToggle" onclick="sideOpen=true;render()">Listone</button>':'')+
   '<nav>'+nav.map(x=>'<button class="'+(tab===x[0]?'on':'')+'"'+
    ' onclick="go(\''+x[0]+'\')">'+x[1]+'</button>').join("")+'</nav>'+
   (S.ready?'<div class="cash"><b>'+S.parts[0].credits+'</b><small>crediti · '+S.my_slots_left+' slot</small></div>':'')+
   '</div><div class="mainScroll">'+start+body+'</div></div></div>';
  if(tab==="mia") initDrag();
  if(tab==="chat"){ const cl=$("#chatList"); if(cl) cl.scrollTop=cl.scrollHeight; }
}
refresh();
</script></body></html>"""


# ------------------------------------------------------------------
#  SERVER
# ------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/api/state"):
            with LOCK:
                self._send(200, json.dumps(snapshot(), ensure_ascii=False))
        else:
            self._send(200, PAGE, "text/html; charset=utf-8")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        try:
            body = json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
        except Exception:
            body = {}
        path = self.path
        try:
            with LOCK:
                if path == "/api/config":
                    STATE["cfg"].update(body.get("cfg", {}))
                    if body.get("alloc"):
                        STATE["alloc"] = body["alloc"]
                    if body.get("preset"):
                        STATE["preset"] = body["preset"]
                    save_state(); out = {"ok": True}
                elif path == "/api/start":
                    STATE["parts"] = fresh_parts()
                    STATE["sold"] = {}
                    STATE["formation"] = {"modulo": "3-4-3", "slots": {}}
                    save_state(); out = {"ok": True}
                elif path == "/api/assign":
                    do_assign(body["id"], body["buyer"], body["price"]); out = {"ok": True}
                elif path == "/api/undo":
                    do_undo(body["id"]); out = {"ok": True}
                elif path == "/api/target":
                    pid = body["id"]
                    STATE["targets"][pid] = (STATE["targets"].get(pid, 0) + 1) % 4
                    save_state(); out = {"ok": True}
                elif path == "/api/eval":
                    e = Engine(STATE)
                    p = next(x for x in STATE["players"] if x["id"] == body["id"])
                    ev = e.evaluate(p)
                    ev["stars"] = STATE["targets"].get(p["id"], 0)
                    out = {"player": p, "ev": ev}
                elif path == "/api/alternatives":
                    b = next((x for x in STATE["players"] if x["id"] == body["id"]), None)
                    out = {"alts": alternatives(b, int(body.get("n", 5))) if b else [],
                           "bought": {"nome": b["nome"], "team": b["team"]} if b else None}
                elif path == "/api/formation":
                    STATE["formation"] = {"modulo": body.get("modulo", "3-4-3"),
                                          "slots": body.get("slots", {})}
                    save_state(); out = {"ok": True}
                elif path == "/api/key":
                    STATE["api_key"] = body.get("key", "").strip(); save_state(); out = {"ok": True}
                elif path == "/api/import":
                    out = {"n": import_listone(body.get("text", ""))}
                elif path == "/api/chat":
                    out = agent_chat(body.get("msg", ""))
                elif path == "/api/agent":
                    kind = body.get("kind")
                    out = agent_strategist() if kind == "strategist" else agent_scout(body["id"], body.get("news"))
                else:
                    out = {"errore": "endpoint sconosciuto"}
        except urllib.error.HTTPError as e:
            out = {"errore": "L'agente ha risposto con errore %s. Controlla la chiave API." % e.code}
        except urllib.error.URLError:
            out = {"errore": "Nessuna connessione: gli agenti servono internet, il resto dell'app no."}
        except Exception as e:
            out = {"errore": str(e)}
        self._send(200, json.dumps(out, ensure_ascii=False))


def tailscale_urls():
    import subprocess
    urls = []
    for cmd in (["tailscale", "ip", "-4"], ["/Applications/Tailscale.app/Contents/MacOS/Tailscale", "ip", "-4"]):
        try:
            o = subprocess.run(cmd, capture_output=True, text=True, timeout=4).stdout.strip()
            for line in o.split("\n"):
                if re.fullmatch(r"100\.\d+\.\d+\.\d+", line.strip()):
                    urls.append("http://%s:%d" % (line.strip(), PORT))
            if urls:
                break
        except Exception:
            continue
    return urls


def lan_url():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close()
        return "http://%s:%d" % (ip, PORT)
    except Exception:
        return None


def main():
    load_state()
    url = "http://127.0.0.1:%d" % PORT
    print("\n  BANCO D'ASTA v%s — fantacalcio Serie A 2026/27" % VERSION)
    print("  " + "-" * 46)
    print("  File in esecuzione:     %s" % os.path.abspath(__file__))
    print("  Su questo dispositivo:  %s" % url)
    lan = lan_url()
    if lan:
        print("  Sulla stessa Wi-Fi:     %s   <- per l'iPad" % lan)
    for t in tailscale_urls():
        print("  Via Tailscale:          %s" % t)
    print("  Listone:                %d giocatori" % len(STATE["players"]))
    print("  Stato salvato in:       %s" % STATE_FILE)
    print("  Ferma il server con Ctrl+C\n")
    try:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    except Exception:
        pass
    try:
        srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    except OSError as e:
        print("  !! Non riesco ad aprire la porta %d: %s" % (PORT, e))
        print("  !! C'e' gia' un'altra copia in esecuzione: chiudila e rilancia.\n")
        return
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  Chiuso. Lo stato dell'asta e' salvato.")


if __name__ == "__main__":
    main()
