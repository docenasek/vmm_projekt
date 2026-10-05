## 2. STŘELECKÁ ÚSPĚŠNOST
Možné cíle projektu
· Aplikace vhodných způsobů předzpracování dat pro jejich následnou validní analýzu
· Výběr příznaků souvisejících s úspěšnosti daného pokusu o branku
· Stanovení souvislostí mezi různými příznaky, popisujícími dosavadní „vývoj“ pokusu (střely)
· Identifikace a interpretace různých skupin pokusů na základě okolních faktorů
· Efektivní vizualizace naměřených multimodálních dat
· … (meze se nekladou :-)

# Datový soubor
shots_outcome_Final.csv – údaje popisující samotnou ránu na branku, situaci, která tomu předcházela,
výsledek (gól či jiné) apod.:
Označení příznaku v
Popis příznaku Poznámka
databázi


id ID zápasu
minute minuta, ve které padla střela
X pokud velikost fotbalového hřiště
je 100x100 jednotek (délka x šířka,
zjednodušená reprezentace), pak
X reprezentuje délku (resp. první
souřadnici místa, odkud vycházela
střela). 0 až 100 jednotek zleva
doprava mezi brankovými čarami
Y Y reprezentuje šířku (resp. druhou
souřadnici místa, odkud vycházela
střela). 0 až 100 mezi postranními
čarami (od outu k outu)
xG xG (=Expected Goal) dané střely
player hráč-střelec
h_a jestli střela padla doma
(v domácím zápase) nebo ne
player_id ID hráče-střelce
situation situace, ze které se střílelo např. OpenPlay, SetPiece,
DirectFreekick, FromCorner
year daná sezóna
shotType část těla, kterou hráč vystřelil např. RightFoot, Head,
LeftFoot, Other
match_id ID daného zápasu
h_team domácí tým
a_team hostující tým
h_goals góly/body domácího týmu
a_goals góly/body hostujícího týmu
date datum zápasu
player_assisted přihrávající hráč (pokud byl)
lastAction akce předcházející střele např. Chipped, Cross,
Pass, TakeOn, Rebound
Result Výsledek: 'BlockedShot', 'Goal',
'MissedShots', 'OwnGoal',
'SavedShot' nebo
'ShotOnPost'


POZOR:
- V datovém souboru se mohou vyskytovat odlehlé hodnoty, chybějící hodnoty měřených
veličin (označené jako např. NaN, ‘-’ apod.), hodnoty nedávající smysl apod.