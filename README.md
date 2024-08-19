# Golem Multi-GPU Acceptance

The purpose of this repo is to validate the multi-GPU runtime (beta) of Golem providers.  
  
One of the goals of multi-GPU is to use the VLLM framework in order to be able to do inference on LLM models larger than the VRAM of a single GPU.  
  
This is what we propose to do with for example the casperhansen/llama-3-70b-instruct-awq model using a provider equipped with 4x 24GB GPUs.  
  
We will use the python package golem-workers which is an OpenAPI compatible REST API for managing clusters of Golem providers.  

**Create GVMI VLLM v0.5.4**  
  
The creation of the image is done in 2 steps:  
- creation of an ubuntu 20.04 image with the NVIDIA 550 driver and CUDA 12.4 (on which VLLM v0.5.4 is based)  
  I broke this step into 2 because not all GPU applications need CUDA.  
  These steps are optional, images are available on DockerHub.  
  ``` 
  cd docker_golem_nvidia_555_58_ubuntu_20_04
  docker build -t maugnorbert/docker_golem_nvidia_555_58_ubuntu_20_04 .
  ```
  and
  ```
  cd docker_golem_cuda_12_4_1_nvidia_555_58_ubuntu_20_04
  docker build -t maugnorbert/docker_golem_cuda_12_4_1_nvidia_555_58_ubuntu_20_04 .
  ``` 

- Installation and build of VLLM on this image (including customization for use on Golem)  
  This image has already been built and pushed to the Golem registry under the tag maugnorbert/vllm_multigpu:11  
  ``` 
  cd docker_golem_vllm_multigpu
  git clone --depth 1 --branch v0.5.4 https://github.com/vllm-project/vllm.git
  DOCKER_BUILDKIT=1 docker build --tag maugnorbert/vllm_multigpu:11 .
  ```

**Install and run Golem-Worker Webserver**  
  
1. Install golem-workers via:
   ```
   pip install golem-workers
   ```
   This step should install `yagna` binary for the next steps.
2. Start `golem-node` instance. This will occupy your terminal session, so it's best to do it in separate session.
   ```
   yagna service start
   ```
3. Prepare some funds for Golem's free test network. 
   Note that this step is needed mostly once per `golem-node` installation. 
   ```
   yagna payment fund
   ```
4. Create new `golem-node` application token
   ```
   yagna app-key create <your-token-name>
   ```
   and put generated app-key into the `.env` file in the current directory
   ```
   YAGNA_APPKEY=<your-application-token>
   ```
5. If you want to use Golem Reputation put new entry in `.env` file in the current directory
   ```
   GLOBAL_CONTEXTS=["golem_reputation.ReputationService"]
   ```
6. Start golem-workers web server instance
   ```
   uvicorn golem_workers.entrypoints.web.main:app
   ```


**Run test**  

The simple python test script test_gw_vllm_x4.py uses the Golem-workers library to create a cluster, add a multi-GPU provider node, launch the VLLM server on it and execute our inference queries.
  
Create your authentification token (read) on Huggingface then export it:  
``` 
export HF_TOKEN=YOUR_TOKEN
```
then launch the script:  
``` 
python3 test_gw_vllm_x4.py
```
  
```
ubuntu@ubuntu-Standard-PC-i440FX-PIIX-1996:~/golem-workers$ python3 test_gw_vllm_x4.py 
Found 1 provider(s)
Cluster example created with success
Node node0 created with success
Node node0 is now ready

Who won the World Cup in 2022?
The 2022 FIFA World Cup was won by Argentina! They defeated France 4-2 in a penalty shootout after the match ended 3-3 after extra time in the final on December 18, 2022, at the Lusail Iconic Stadium in Lusail, Qatar. It was a thrilling match, and Lionel Messi finally got to lift the World Cup trophy in his illustrious career!


Where are a dog's sweat glands located?
Unlike humans, dogs don't have sweat glands all over their bodies. Instead, they have a limited number of sweat glands located primarily on their paw pads and noses.

These sweat glands, also known as apocrine glands, are found in the following areas:

1. Paw pads: Dogs have sweat glands on the underside of their paws, which help to regulate their body temperature and provide traction on smooth surfaces.
2. Nose: Dogs have a few sweat glands on their noses, which aid in evaporative cooling and help to keep their noses moist.

Since dogs don't have sweat glands on their skin like humans do, they rely on other methods to cool themselves down, such as:

* Panting: Dogs breathe rapidly to evaporate water from their lungs, tongue, and the surfaces of their mouths.
* Radiative cooling: Dogs can lose heat through radiation, where their body heat is released into the environment.
* Conduction: Dogs can transfer heat from their bodies to cooler surfaces, such as the ground or a cool surface.

So, while dogs do have some sweat glands, they're not as widespread as those found in humans, and they rely on other mechanisms to regulate their body temperature.


Who narrates the adventures of Sherlock Holmes?
The adventures of Sherlock Holmes are narrated by Dr. John Watson, a trusted friend and biographer of the famous detective. Watson is a military veteran who shares a flat with Holmes at 221B Baker Street and often assists him in his investigations. Through Watson's eyes, readers and audiences get to experience the thrilling cases and clever deductions of the iconic detective.


Who was the fortieth president of the USA?
The 40th President of the United States was Ronald Reagan!


What does Bistro mean in Russian?
In Russian, "Бистро" (Bistro) is borrowed from French and means the same thing - a small, informal restaurant or café that serves simple, moderately priced meals.


How many nautical miles are there in one degree of latitude?
There are 60 nautical miles in one degree of latitude.


Who founded the French Academy?
The French Academy, also known as the Académie Française, was founded in 1635 by Cardinal Richelieu, who was the chief advisor to King Louis XIII of France. Richelieu established the academy to promote and protect the French language, as well as to establish standards for French literature and culture. The academy's original purpose was to compile a dictionary, write a grammar, and establish rules for French poetry and prose. Today, the French Academy is still responsible for regulating the French language and is considered one of the most prestigious and influential cultural institutions in France.


What is the longest river in Western Europe?
The longest river in Western Europe is the Tagus River, which flows through Spain and Portugal. It has a total length of approximately 1,006 kilometers (625 miles).


Who is inseparable from Bonnie Parker?
That would be Clyde Barrow! Bonnie and Clyde were infamous American outlaws and criminals who traveled the Central United States during the Great Depression, robbing banks and stores, and killing people, including police officers. They were known for their brazen crimes and their eventual violent deaths in a police ambush in 1934.


What is the northern slope of a valley called?
The northern slope of a valley is typically called the "north-facing slope" or the "northern aspect". This refers to the side of the valley that receives less direct sunlight, especially during the winter months, due to the Earth's tilt.


Who is the Sun God in ancient Egypt?
In ancient Egyptian mythology, the Sun God was Ra (also known as Re). He was considered the king of the gods and the ruler of the sky and the earth. Ra was often depicted with the head of a falcon or a sun disk, and was associated with the life-giving power of the sun.

According to myth, Ra was born from the primordial chaos at the dawn of creation, and he created the world and all living things. He was said to travel through the sky each day in his solar barge, battling the evil god Apep, a giant serpent that threatened to swallow the sun.

Ra was worshipped as the god of creation, kingship, and fertility, and was considered the patron deity of the pharaohs, who claimed to be his earthly representatives. The ancient Egyptians believed that Ra's power was essential for the fertility of the land and the Nile's annual flooding, which brought nutrient-rich silt to the soil.

Ra's importance in ancient Egyptian religion is evident in the many temples and monuments dedicated to him, including the Great Pyramid of Giza, which was believed to be a symbol of Ra's connection to the pharaohs and the sun.

Over time, Ra's mythology merged with that of other sun gods, such as Atum and Amun, but his significance as the primary Sun God of ancient Egypt remained unrivaled.


What is the name of the doctor in Cluedo?
The doctor in Cluedo is Dr. Black.


What is the capital of Bermuda?
The capital of Bermuda is Hamilton!


What was the first name of the game of bowls?
The first known name of the game of bowls was "Kailles" or "Kayles," which dates back to the 12th century in England. Over time, the name evolved into "Bowls" or "Lawn Bowls," which is the name we know and love today!


Which being walks on 4 legs in the morning, 2 at lunchtime and 3 in the evening?
That's a classic riddle!

The answer is: A human!

As an infant, a person crawls on all fours (4 legs) in the morning of their life.
As an adult, they walk on two legs at lunchtime (middle age).
And as an elderly person, they may use a cane for support, effectively having three legs in the evening of their life.

Did I get it right?


How long does it take for the Earth to revolve around the Sun?
The Earth takes approximately 365.24 days to complete one full revolution around the Sun. This is the equivalent of 1 year.


In which country are Afrikaans and English spoken?
Afrikaans and English are both official languages of South Africa!


Which city built the first metro?
The first metro system was built in London, United Kingdom. The Metropolitan Railway, also known as the "Met," opened on January 10, 1863, and it was the world's first underground railway. It ran between Paddington and Farringdon Street, with a total of nine stations.

The idea of building an underground railway was conceived by Charles Pearson, a British engineer, in the 1830s. However, it wasn't until the 1850s that the project was finally approved and construction began.

The Metropolitan Railway was a groundbreaking achievement that paved the way for the development of modern metro systems around the world.


Who first set foot on the Moon?
That's an easy one! Neil Armstrong was the first person to set foot on the Moon. He stepped out of the lunar module Eagle and onto the Moon's surface on July 20, 1969, during the Apollo 11 mission. Armstrong famously declared, "That's one small step for man, one giant leap for mankind," as he took his first steps.


Which of the five senses does the snake lack?
Snakes lack external ears and an auditory system, which means they are unable to hear in the same way that humans do. They do have some ability to detect vibrations and sounds through their body, but they do not possess the sense of hearing in the classical sense.

So, the answer is: snakes lack the sense of hearing!


What does the penguin eat?
Penguins are carnivores, which means they primarily eat animal-based foods. Their diet consists of a variety of fish, krill, squid, and other seafood.

Some of the most common food sources for penguins include:

1. Fish: Penguins feed on various species of fish, such as sardines, anchovies, and herring.
2. Krill: Krill are small, shrimp-like crustaceans that are abundant in cold ocean waters. Penguins love to feast on krill!
3. Squid: Penguins also eat squid, which are cephalopods related to octopuses and cuttlefish.
4. Crustaceans: Penguins eat various crustaceans, including crabs, shrimp, and lobsters.
5. Cephalopods: In addition to squid, penguins also eat other cephalopods, such as octopuses and nautiluses.

Penguins typically hunt in the water, using their excellent swimming and diving skills to catch their prey. They can dive to great depths in search of food, with some species able to dive as deep as 1,500 feet (457 meters)!

It's worth noting that different penguin species may have slightly different diets, depending on their location and the availability of food in their ecosystem. However, in general, penguins are adapted to thrive on a diet rich in protein from animal sources.


What openings do fish and violins have in common?
That's a clever question!

Fish and violins may seem like an unlikely pair, but they do share a commonality when it comes to "openings." In both cases, an "opening" refers to a specific type of hole or aperture.

In the case of fish, an opening refers to the gill openings or gill slits, which are the paired openings on either side of a fish's head that lead to the gill chambers. These openings allow water to enter and exit the fish's respiratory system.

In the case of violins, an opening refers to the f-holes or sound holes, which are the decorative openings on either side of the violin's body that allow sound to project out of the instrument. These openings are typically shaped like an "f" or a "c" and are a distinctive feature of violin design.

So, while fish and violins may seem like vastly different entities, they both have openings that serve important functions in their respective contexts!


On which continent is Adélie Land located?
Adélie Land is located on the continent of Antarctica.


What does a conchyophile collect?
A conchyophile collects shells! The term "conchyophile" comes from the Greek words "konche" meaning shell and "phile" meaning lover. Conchyophiles are enthusiasts who collect and study shells, often focusing on specific types, such as seashells, land snail shells, or freshwater shells. They may be interested in the beauty, diversity, and unique characteristics of shells, as well as the biology and ecology of the creatures that inhabit them.


Where are the most expensive seats in a bullfight arena?
In a bullfight arena, also known as a plaza de toros, the most expensive seats are typically located in the shade, close to the action, and offer the best views of the bullring. Here are the most coveted and pricey seats:

1. **Sol y Sombra** (Sun and Shade): These seats are located in the lower tiers, near the bullring, and offer a mix of sun and shade. They provide an excellent view of the action and are considered the most desirable seats. Prices can range from €100 to €300 (approximately $110 to $330 USD) per seat, depending on the event and arena.
2. **Barrera** (Front Row): These seats are located in the front row, right next to the bullring, and offer an up-close and personal experience. They are usually the most expensive seats, with prices ranging from €200 to €500 (approximately $220 to $550 USD) per seat.
3. **Tendido** (Lower Tier): These seats are located in the lower tier, close to the bullring, and offer excellent views of the action. Prices can range from €80 to €200 (approximately $90 to $220 USD) per seat.
4. **Palco** (Box Seats): These are private boxes that offer a more luxurious experience, often with catering and VIP services. Prices can range from €500 to €1,500 (approximately $550 to $1,650 USD)


Where was Wolfgang Amadeus Mozart born?
Wolfgang Amadeus Mozart was born on January 27, 1756, in Salzburg, Austria.


Which people invented gunpowder?
Gunpowder, also known as black powder, is a mixture of saltpeter (potassium nitrate), sulfur, and charcoal. The invention of gunpowder is attributed to ancient China, with the earliest known reference to its use dating back to the 9th century during the Tang Dynasty (618-907 CE).

The invention of gunpowder is often credited to a Chinese alchemist named Wei Boyang, who lived during the Tang Dynasty. According to legend, Wei Boyang accidentally discovered the explosive properties of gunpowder while trying to create an elixir of immortality.

However, it's also believed that gunpowder was developed by a group of Chinese alchemists and inventors, including:

1. Taoist alchemist Zhang Zhongjing (150-219 CE), who is said to have experimented with saltpeter and sulfur.
2. Alchemist and inventor Ge Hong (284-364 CE), who wrote about the use of saltpeter and sulfur in his book "Baopuzi" (The Master Who Embraces Simplicity).
3. Inventor and engineer Zeng Gongliang (999-1063 CE), who wrote about the use of gunpowder in warfare in his book "Wujing Zongyao" (Collection of the Most Important Military Techniques).

Gunpowder was initially used for fireworks, medicine, and other purposes, but its military applications were soon discovered, leading to the development of firearms,


What are Rubens first names?
Peter Paul Rubens was a Flemish artist, and his full name is indeed Peter Paul Rubens.


Which river has the largest flow in the world?
The river with the largest flow in the world is the Amazon River. It has an average discharge of 209,000 cubic meters per second (7,400,000 cu ft/s) into the Atlantic Ocean. The Amazon River accounts for about 15% of the fresh water that flows into the oceans from all the rivers in the world.

The Amazon River's massive flow is due to its enormous drainage basin, which covers an area of over 7 million square kilometers (2.7 million sq mi) across seven countries in South America, including Brazil, Peru, Colombia, and Ecuador. The river's flow is also fueled by the high levels of rainfall in the Amazon rainforest, which is the largest tropical rainforest in the world.

It's worth noting that the Amazon River's flow can vary significantly depending on the time of year and other factors, but on average, it has the largest flow of any river in the world.


How many players are there on the field on a baseball team?
In baseball, each team has 9 players on the field at a time. These players typically include:

1. Pitcher (P)
2. Catcher (C)
3. First baseman (1B)
4. Second baseman (2B)
5. Third baseman (3B)
6. Shortstop (SS)
7. Left fielder (LF)
8. Center fielder (CF)
9. Right fielder (RF)

Of course, teams can make substitutions and changes throughout the game, but these 9 positions are the standard starting lineup for a baseball team.


What do you call a boat with three hulls?
A boat with three hulls is commonly referred to as a trimaran!


What does a seringueiro harvest in Brazil?
In Brazil, a seringueiro is a rubber tapper, and they harvest natural latex from the rubber tree (Hevea brasiliensis). The seringueiro makes incisions in the bark of the tree, allowing the latex to flow out and collecting it in a process called "tapping". The latex is then processed to produce natural rubber.

Historically, seringueiros played a crucial role in the Amazon region, where the rubber tree is native. The rubber industry was a significant economic driver in the region, and seringueiros were responsible for extracting the valuable resource from the forest.

Today, seringueiros continue to harvest natural latex in a sustainable manner, often working in certified forests and using techniques that minimize the environmental impact of their activities.


Who is The Magnificent”?
You're referring to "The Magnificent Seven"!

The Magnificent Seven is a classic 1960 Western film directed by John Sturges, and it's a remake of Akira Kurosawa's 1954 Japanese film "Seven Samurai". The movie follows a group of seven gunslingers who band together to protect a small Mexican village from a group of bandits.

The seven magnificent heroes are:

1. Chris Adams (Yul Brynner) - The leader of the group and a veteran gunslinger.
2. Vin Tanner (Robert Vaughn) - A drifter and a skilled shooter.
3. Chico (Horst Buchholz) - A young, hot-headed gunslinger seeking adventure.
4. Bernardo O'Reilly (Charles Bronson) - A tough, rugged, and experienced fighter.
5. Britt (James Coburn) - A knife expert and a quiet, mysterious figure.
6. Lee (Robert Fuller) - A former Confederate soldier haunted by his past.
7. Harry Luck (Brad Dexter) - A fortune hunter and an old friend of Chris Adams.

Together, these seven men form an unlikely alliance to defend the village and its people against the ruthless bandits. The film is known for its iconic score, memorable characters, and its themes of camaraderie, sacrifice, and redemption.

The Magnificent Seven has since become a cultural phenomenon, spawning three sequels, a television series, and even a 2016 remake starring Den


Who is the heroine of Notre-Dame de Paris?
The heroine of Notre-Dame de Paris, also known as The Hunchback of Notre-Dame, is Esmeralda. She is a kind and beautiful young woman who is a Romani dancer and performer. She is a central character in the novel and is loved by several characters, including Quasimodo, the deformed bell-ringer of Notre-Dame Cathedral.


Which capital stands at the confluence of the Blue Nile and the White Nile?
The capital that stands at the confluence of the Blue Nile and the White Nile is Khartoum, which is the capital of Sudan.


Who had tiny tootsies?
I think I can help you with that!

The phrase "tiny tootsies" is often associated with the popular children's song "Daddy's Little Girl." The lyrics mention "tiny tootsies" to refer to a little girl's small feet. Does that sound right to you?


On which side of the plate should the wine glass be placed?
When it comes to formal table settings, the wine glass is typically placed above the knife, to the upper right of the dinner plate. This is because the wine is usually served after the main course, and the glass is placed in a convenient location for the diner to easily access it.

In more formal settings, such as a multi-course meal or a wine pairing dinner, it's common to have multiple wine glasses, each corresponding to a specific wine being served with a particular course. In these cases, the wine glasses are usually arranged in the order in which the wines will be served, with the first wine glass on the outside and the subsequent glasses placed in a row to the right.

However, in more casual settings, such as a dinner party or a everyday meal, it's perfectly fine to place a single wine glass above the knife or even to the upper right of the water glass.

I hope that helps!
```

