#!/usr/bin/env python3
"""Insert Dua Lipa's favorite spots into index.html.

Tags each place with dl:true. Adds a "Dua Lipa's Favorites" tab to city pages,
new cities (Antwerp, Austin, Bangkok, Brussels, Cornwall, Hong Kong, Kuala Lumpur,
Marseille, Nashville, Prishtina, Tirana, Singapore) plus their META/COORDS/REGIONS
and new CCODES (Belgium, Thailand, Hong Kong, Malaysia, Kosovo, Singapore).
"""
import json, re, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / 'index.html'

# (city, name, category, description, rating)
PLACES_DATA = [
    ("Mexico City", "Santo Taco", "Food", "The steak trompo is extraordinary, but then again, so is nearly everything on the menu. Make sure to not look too long at the menu -- order and get into it!", 4.6),
    ("Melbourne", "The Paperback Bookshop", "Places to See", "Paperback in Melbourne is a tiny bookshop in the CBD with a clear sense of what it loves. Literary fiction, translated literature, small press titles. The staff recommendations are worth trusting -- it's a great browse.", 4.8),
    ("Mexico City", "Maximo Bistrot", "Food", "Maximo Bistrot feels like the kind of restaurant that anchors the city cuisine-wise. The cooking here is brilliant technically, but it never feels cold or distant. Farm-to-table done with personality. The bone marrow preparation alone is worth it.", 4.5),
    ("Tokyo", "epulor", "Nightlife", "A really quiet little neighbourhood cafe a little off the beaten track. Vinyl play on into the evening, where coffee can turn into a glass of natural wine.", 4.3),
    ("Amsterdam", "de Willem", "Food", "The small plates, the perfect light at sunset, the community vibe -- the place gives you options rather than deciding the mood for you.", 4.3),
    ("Barcelona", "Cañete", "Food", "Bar Canete in Barcelona is old-school tapas with confidence. Iberian ham, white anchovies, a glass of something cold. It has been there since 1935 and shows no signs of slowing down. I love to go for lunch.", 4.6),
    ("Berlin", "Julius Ernst", "Food", "Julius Ernst in Berlin are extremely sophisticated small plates in a very Berlin atmosphere that is somehow both very relaxed and full of intention.", 3.7),
    ("Tokyo", "Cignale Enoteca", "Food", "Cignale is an Italian wine bar in Tokyo and it is fantastic. Really good natural wine, beautiful tasting menu. It's Italian cuisine with a Japanese sensibility. The juxtaposition really works.", 4.7),
    ("New York City", "Joyface", "Nightlife", "Joy Face is a great spot for cocktails and loitering. It's the kind of neighbourhood cocktail bar you want to stumble into and then stay in for three hours without realising.", 3.3),
    ("Mexico City", "Café Tormenta", "Food", "Tormenta gets my vote for best local Mexican-inspired drinks and pastries -- try the local sodas for something you won't find elsewhere.", 3.8),
    ("Mexico City", "Em", "Food", "Em is Lucho Martínez doing what he does best, which is taking Mexican ingredients seriously and making something completely original from them. It's probably the most exciting vegetable cooking I have experienced. You will not miss meat.", 4.2),
    ("Tokyo", "WOMB", "Nightlife", "One of the great Tokyo clubs. The sound system is legendary and the programming has always been serious about underground electronic music. Tokyo has a specific relationship with club culture and Womb is right at the centre of it.", 3.9),
    ("Berlin", "Renate", "Nightlife", "To me, Renate in Berlin is one of the most special clubs in the world. It's in an old apartment building and each room feels different, each floor has its own atmosphere. You can get completely lost in there. Go and let the night happen.", 4.5),
    ("New York City", "Public Records", "Nightlife", "Public Records in Brooklyn is known for taking music seriously in a way that I really respect. It's got a crazy custom sound system, really well curated acts, and a thoughtful food programme to accompany. Multiple rooms with a different vibe. You've got options.", 4.3),
    ("New York City", "Gabriela", "Nightlife", "Gabriela is a great late night spot in New York. I love the music and the crowd is mixed and fun with a certain warmth to it that you don't always find in New York nightlife. A real one.", 3.1),
    ("Prishtina", "Sunny Hill Festival", "Nightlife", "Sunny Hill is my home festival. The fact that it exists in Prishtina, built in Kosovo, means everything to me. This is where I go to really party.", 4.3),
    ("London", "KOKO", "Nightlife", "This one is a bit nostalgic for me because Koko used to be right around the corner from where I lived in Camden. I would go there to discover new acts, and as a consequence, I've had too many nights out at Koko to remember.", 4.4),
    ("Mexico City", "Club San Luis", "Nightlife", "Club San Luis is exactly where I want to end a night in Mexico City. It's a proper club. The music gets good, the crowd is there for it, and there's this specific Mexico City energy in the room that's hard to describe -- you just have to feel it.", 3.4),
    ("Bangkok", "House of HEALS", "Nightlife", "I've been to a lot of drag nights around the world. But House of Heals in Bangkok is one I talk about. The crowd is electric, and it has that specific feeling of being very proud of what it stands for.", 4.7),
    ("Rio de Janeiro", "Matiz", "Nightlife", "This is where the music is good, the caipirinhas are great, and the crowd has a mix of music genres that means if you want to just listen you can or, of course, you can get up and dance.", 3.7),
    ("Austin", "Broken Spoke", "Nightlife", "A genuine piece of American music history. Broken Spoke has been there since 1964 and hasn't been changed at all. Two-stepping to live country music in a room that still looks exactly the same as when it opened. Nothing like it.", 4.2),
    ("Istanbul", "Kontra Plak", "Places to See", "Kontra Plak in Istanbul is a cultural resource as much as a record shop and spending time there changes what you know about music.", 4.6),
    ("Stockholm", "Pet Sounds", "Places to See", "Pet Sounds in Stockholm has been going since 1975 and is still one of the best record shops in Europe. The selection is eclectic and highly intentional, the prices are reasonable, and the team are passionate and there to guide you.", 4.5),
    ("Brussels", "Tropicall Records", "Places to See", "Tropicall in Brussels has a focus on tropical, African, and world music that is unlike any other shop I've been to. The knowledge behind the selection is real and the things you find there can be extraordinary. A record pilgrim's destination.", 4.8),
    ("Lisbon", "Amor Records", "Places to See", "Amor Records in Lisbon is a great one. The selection skews toward Portuguese and European music from the 60s through to the 90s and the curation is really considered.", 4.7),
    ("Rio de Janeiro", "Tropicália Discos", "Places to See", "Tropicalia Discos in Rio is a beautiful little record shop that understands Brazilian music across all its forms. Samba, MPB, bossa nova, rare pressings you can't find online. This shop makes you grateful vinyl survived.", 4.9),
    ("Berlin", "Hard Wax", "Places to See", "Hard Wax in Berlin is the definitive electronic music record shop. Dub techno, house, jungle, all of it in one room with super knowledgeable staff. An institution.", 4.7),
    ("Los Angeles", "Amoeba Music", "Places to See", "Amoeba in Hollywood is one of the greatest record shops to ever exist. The depth and range of the collection is staggering -- I could spend an entire day there without covering everything.", 4.8),
    ("Kingston", "Rockers International Records", "Places to See", "Rockers International in Kingston is reggae history in a physical space. The selection goes deep into roots and dancehall and stepping inside feels like being at the source of something important and worth prioritising.", 4.3),
    ("Melbourne", "Plug Seven Records", "Places to See", "One of my favourite places for vinyl is Plug Seven record shop in Melbourne, because of its eclectic selections. It also has 7 inches as collectibles and they're often buying rare collections.", 4.8),
    ("London", "Rough Trade East", "Places to See", "Rough Trade East in Brick Lane has stayed completely relevant. They still break new music, they have an incredible live programme, and the selection across new releases and archive is always excellent. I've been going for years.", 4.7),
    ("Mexico City", "Roma Records", "Places to See", "La Roma Records is tucked into the Roma neighbourhood in Mexico City. Mexican and Latin American records, great staff knowledge, warm atmosphere.", 4.4),
    ("Tokyo", "Tower Records Shibuya", "Places to See", "Tower Records in Tokyo is still one of the most exciting record shopping experiences I've had. The selection across every genre is extraordinary and you will find things there that you simply cannot find anywhere else. I always come out with too much to carry.", 4.4),
    ("Edinburgh", "Rare Birds Book Shop", "Places to See", "Rare Birds in Edinburgh is a famous independent bookshop and subscription service that's dedicated exclusively to fiction written by women. The name itself comes from an old saying the founder Rachel Wood always loved -- a rare bird being described as an exceptional person or thing, a rarity -- so it refers to both the books and the people who wrote them. Which, hopefully, will eventually become a little less rare.", 4.9),
    ("Marseille", "Ensemble", "Places to See", "Ensemble in Marseille is a beautifully curated bookshop that reflects the city it's in. Mediterranean literature, art books, zines, a distinctive point of view. Makes you want to read everything at once.", 5.0),
    ("Porto", "Livraria Lello", "Places to See", "Livraria Lello in Porto is one of the most beautiful bookshops in the world. The carved wooden staircase, the stained glass ceiling, the whole building. Because they also are a publisher, it's a living bookshop. The insider tip is to get a ticket to the downstairs gallery space that houses rare collections.", 4.0),
    ("Kuala Lumpur", "Tintabudi Bookshop", "Places to See", "Tintabudi in Kuala Lumpur is a beautiful independent bookshop and creative space doing something important for the reading culture of the city. The selection of Southeast Asian literature is particularly strong.", 4.7),
    ("Antwerp", "De Groene Waterman", "Places to See", "De Groene Waterman in Antwerp is one of those bookshops that makes you want to learn another language just so you can read more of what's on the shelves. Old and new in a beautiful building.", 4.7),
    ("Cape Town", "Clarke's Bookshop", "Places to See", "Clarkes in Cape Town is a bookshop that feels like it grew organically out of the neighbourhood. African literature, independent publishers, and a sense that the people running it care deeply about what they're putting on the shelves.", 4.6),
    ("New York City", "Albertine", "Places to See", "Albertine is the French bookshop in the French Cultural Services building on Fifth Avenue in New York and it is extraordinary. French literature in the original and in translation, beautifully displayed. It feels like a small piece of Paris in midtown Manhattan.", 4.6),
    ("Mexico City", "La Americana", "Places to See", "Our Service95 Book Club hosted a Book Tasting in Mexico City last year at this little independent bookstore cafe called La Americana. Definitely the vibe for a chill day of reading.", 4.1),
    ("Hong Kong", "Boundary Bookstore", "Places to See", "Boundary Bookstore in Hong Kong is a special one. In a city known for moving fast, it's calm and thoughtful. The store highlights Chinese literature from the diaspora, specifically covering Malaysia, Taiwan, Macau, and Hong Kong, as well as some select English titles.", 4.9),
    ("London", "Brick Lane Bookshop", "Places to See", "Brick Lane Bookshop has been on that street for decades and it holds its own against everything that has changed around it. A proper community bookshop with range and a team who you can tell really love books.", 4.7),
    ("London", "Lala Books", "Places to See", "La La Books in London is one of the most beautifully curated independent bookshops I've been to. The selection is really considered and specific. A wonderful place to spend an afternoon.", 4.8),
    ("Sydney", "10 William St", "Nightlife", "10 William Street in Paddington is one of those places that just gets it right. Great Italian-influenced natural wine list, brilliant food, and a room that feels like it belongs somewhere in Rome or Naples.", None),
    ("Sydney", "Ester Restaurant", "Food", "Ester in Sydney is wood-fired cooking and excellent natural wine in a room that always has great energy. The menu changes constantly and there's a real confidence to the cooking that I love. A Sydney essential.", 4.6),
    ("Melbourne", "Hope St Radio", "Nightlife", "Hope Street Radio in Melbourne has great music, a really considered wine list, and an atmosphere that manages to be both cool and welcoming.", 4.2),
    ("Barcelona", "Can Cisa/Bar Brutal", "Nightlife", "Honestly, just trust whoever's behind the bar. But if the charred squid is on -- and often it is -- get that immediately. And then let them pick the wine. For me that's the whole point of going somewhere like that.", 4.2),
    ("New York City", "Le Dive", "Nightlife", "Le Dive has stylish vibes, generous pours and for that reason it's always abuzz. In the summer, people eat, drink and sprawl onto the street. The kitchen closes at midnight so make sure to get their fries and a final glass before then.", 4.0),
    ("New York City", "The Four Horsemen", "Nightlife", "Four Horsemen in Williamsburg is the natural wine bar that created the template for so many places that came after it. The list and the food stand entirely on their own. A classic for a reason.", 4.6),
    ("London", "Hector's", "Nightlife", "Hectors is a neighbourhood wine bar that punches well above its weight. The list is focused and really well chosen and the food is exactly what you want alongside a good glass of something orange and natural. A great local.", 4.5),
    ("London", "40 Maltby Street", "Nightlife", "40 Maltby Street is in a railway arch in Bermondsey and it is one of my favourite wine places in London. The list is serious, the food is simple and excellent, and the whole thing feels like a proper insider find. Go on a Saturday when they do lunch.", 4.7),
    ("Copenhagen", "Pompette", "Nightlife", "Pompette in Nørrebro literally means tipsy in French, and that's exactly what's going to happen. The whole reason it exists is because the founder thought people in Copenhagen were paying too much for natural wine and wanted to fix that, so the prices are honest, which is rare for a wine bar like this. Orange wine, funky bottles, snacks, street-side tables. Start there and see where the night takes you.", 4.5),
    ("Paris", "Early June", "Food", "You never know what you're walking into, and Camille is so passionate about not just making delicious food and curating wines, but bringing a community of chefs and those who enjoy their food together.", 4.3),
    ("Cornwall", "Lovetts", "Nightlife", "You know what, curveball, but I think Lovetts in Cornwall in the UK is a hidden gem that more people should know about. It has some of the best natural wine I've tried.", 4.5),
    ("Bangkok", "Mod Kaew Wine Bar", "Nightlife", "Natural wine in Thailand done with real knowledge and passion. The selection is interesting and the snacks are great. Proof that the natural wine world has expanded to all corners.", 4.5),
    ("Barcelona", "Gresca", "Food", "Natural wine and modern Catalan cooking done in a way that feels effortless. A long dinner, great wine, this is a restaurant that might restore your trust in tasting menus.", 4.0),
    ("New Orleans", "Preservation Hall", "Nightlife", "Preservation Hall is the heartbeat of New Orleans jazz. It's small, it's loud, and the musicians are extraordinary. There are no seats, no drinks, just pure live music in a space that has been doing this since 1961. You will not stand still.", 4.7),
    ("Kingston", "Kingston Dub Club", "Nightlife", "The Kingston Dub Club is a unique experience. Held outdoors on a hillside on Sunday evenings, the sound is old-school reggae and dub played on a real sound system with the whole of Kingston below you.", 4.7),
    ("Milan", "Dal Bolognese Milano", "Food", "Dal Bolognese in Milan is where you go when you want to feel Italian for an evening. The tagliatelle al ragu is the single best version of that dish I've had. A classic for a reason.", 4.3),
    ("Houston", "Nancy's Hustle", "Food", "Nancy's Hustle in Houston surprised me. The wine list is one of the best I've seen in America and the food backs it up. It's a date night restaurant in the truest sense: somewhere that makes the other person feel like you went to real effort.", None),
    ("Madrid", "Corral de la Morería", "Nightlife", "Corral De La Moreria is one of Madrid's most iconic flamenco tablaos and it has never disappointed me. You eat, you drink, and then the show begins and everything stops. The dancers are extraordinary.", None),
    ("Sydney", "Cam's Kiosk (Cafe & Bar)", "Food", "Cam's Kiosk is a genuinely joyful restaurant and I think that matters more than you'd expect. It's relaxed and the food is brilliant. One of my favourite dinner experiences in Australia.", None),
    ("London", "The Dreamery", "Food", "The Dreamery is a tiny, psychedelic jewel box tucked away in De Beauvoir. It's the kind of place where the glowing ceiling mural and stainless steel curves do half the work for you. Between the artisanal scoops and low-intervention wine, everything is considered but nothing feels forced -- the ultimate \"if you know, you know\" spot for a date.", None),
    ("Madrid", "Sala de Despiece", "Food", "Sala De Despiece in Madrid is unlike anywhere I've been. You stand at the counter, you point at what you want, it arrives in seconds. The quality is extraordinary and there's something about that format that makes the whole night feel more alive.", None),
    ("Paris", "Bistrot Des Tournelles", "Food", "I mean you can't beat a bit of candlelit romance, and if you're doing it right, it's Bistrot des Tournelles in Paris all the way. Soft, sexy, and very classic. Great wine list.", None),
    ("London", "Beigel Bake", "Food", "Beigel Bake on Brick Lane has been an institution since 1974. It's open 24/7 and that matters at 2am. The salt beef beigel is the one. The longest-standing queue in East London is always worth it.", 4.4),
    ("Ibiza", "Can Gourmet Eivissa", "Food", "Can Gourmet in Ibiza is the local secret. Everything you'd want for a picnic or a late-night bite: local cheese, cured meats, the best bread. An antidote to the more obvious side of the island.", 4.7),
    ("Nashville", "Dino's Bar & Grill", "Nightlife", "Dino's is a Nashville dive bar and it's everything I want from a dive bar. Cold beer, a great jukebox, and the kind of atmosphere that makes you feel like you could stay all night. And you probably will.", 4.6),
    ("Prishtina", "Proper Pizza", "Food", "Proper Pizza is exactly what it says it is. In Prishtina, having pizza this good probably surprises a lot of people. The crust is right, the toppings are good, and it's always full of people having a great time.", 4.2),
    ("Tokyo", "Narukiyo", "Food", "You walk in and you have absolutely no idea what's about to happen. There's no menu, the owner just starts talking to you and before you know it food that you didn't order is arriving and it's some of the best things you've eaten. You just have to surrender to it completely. That's the whole experience.", 4.2),
    ("New York City", "Montague Diner", "Food", "The Montague Diner is exactly the New York diner that people imagine when they imagine a New York diner. Open late, no pretension, the kind of comfort food a city should have available at any hour.", 4.3),
    ("Madrid", "Chocolatería San Ginés", "Food", "San Gines has been open since 1894. I believe the churros with hot chocolate there is one of the great food rituals of the world. Go after midnight.", 4.3),
    ("Singapore", "Maxwell Food Centre", "Food", "A true Singaporean haven.", 4.4),
    ("Bangkok", "Raan Jay Fai", "Food", "Go to Jay Fai. It's street food, it's Michelin-starred, and the woman running it has been cooking on that same street corner since the 1980s in ski goggles to protect her eyes from the charcoal. They open and stay open til the food runs out. Do not miss the crab omelette.", 3.6),
    ("Bangkok", "Haawm", "Food", "Haawm is Bangkok at its absolute best. The grilled meats, the sticky rice, the sauces. It's the kind of meal that you're still thinking about on the plane home and honestly probably after that too.", 4.8),
    ("Mexico City", "Hanky Panky Cocktail Bar", "Nightlife", "Hanky Panky is a speakeasy-style cocktail bar that is absolutely worth the slight effort of getting through the door. The mezcal cocktails are some of the best I've had anywhere. Small, intimate, and very much a place for the later part of the night.", 4.2),
    ("Mexico City", "Le Tachinomi Desu", "Nightlife", "Le Tachinomi Desu is a Japanese standing bar in the middle of Mexico City, which should not work as well as it does. Excellent sake, really good snacks, one of those perfect little surprises that is so on brand for Mexico City.", 4.6),
    ("Mexico City", "Museo Tamayo Arte Contemporáneo", "Places to See", "Museo Tamayo is one of my favourite contemporary art museums in Latin America. The building is beautiful and the collection goes from Tamayo himself through to international contemporary work. It's also never so crowded that you can't actually look at things properly.", 4.5),
    ("Mexico City", "Frida Kahlo Museum", "Places to See", "The Frida Kahlo Museum is her house and everything in it is still as she left it. Her art is obviously iconic but being inside that space and understanding where she actually made it changes how you see the work.", 4.5),
    ("Mexico City", "Casa Estudio Luis Barragán", "Places to See", "Casa Luis Barragan is a UNESCO heritage site and it looks like a place where a genius lived. The way light moves through those spaces at different times of day is extraordinary. It's architecture as emotion. One of my favourite places in the world.", 4.3),
    ("Mexico City", "Tacos del Valle (Roma Norte)", "Food", "Tacos del Valle is the one you go to late, when the night has been long and you need something delicious. It's my favourite late night taco situation in the city. The suadero is my go-to.", 4.4),
    ("Mexico City", "Pujol", "Food", "Pujol is simply one of the best restaurants in the world. The mole madre has been cooking for years and is such a perfect representation of what Mexican cuisine is.", 4.4),
    ("Mexico City", "Contramar", "Food", "I get straight off the plane and go straight to Contramar. I love the agua chile, the tuna tostada, a mezcalita de maijca, the vibe, just everything. Start there and build the rest of the day around it. Everything else in Mexico City makes more sense after being in Contramar.", 4.5),
    ("Tokyo", "INC cocktails", "Nightlife", "Inc is the kind of cocktail bar where you hand yourself over to the bartender and trust them entirely. The menu is creative without being unhinged. I always have one drink and immediately want another.", 4.1),
    ("Tokyo", "Grandfather's bar", "Nightlife", "Grandfathers is the bar I always end up in on my last night in Tokyo. It has this warm, unhurried energy that feels like the city knows you're leaving and wants to give you a good send-off. The whisky list is excellent.", 4.6),
    ("Tokyo", "AMORE Vintage AOYAMA", "Places to See", "Amore Vintage is genuinely one of the best vintage experiences anywhere I have ever been. The range is extraordinary and I go every time I'm in Tokyo. I always find something I completely didn't expect.", None),
    ("Tokyo", "Vintage QOO", "Places to See", "QOO has an incredible density of great pieces for a relatively small space. Japanese vintage denim, workwear, Americana.", 5.0),
    ("Tokyo", "Archive Store", "Places to See", "Archive Store knows exactly what it is and does it perfectly. If you're serious about vintage, you need to spend a lot of time here. The stock turns over constantly and the team will help you find what you're looking for.", 4.5),
    ("Tokyo", "LAILA TOKIO", "Places to See", "Laila is one of the best fashion archive shops in Tokyo and that is saying something in a city full of incredible vintage stores. The curation is very specific and very considered.", None),
    ("Tokyo", "Gōtoku-ji", "Places to See", "Gotokuji is the lucky cat temple and I cannot fully explain why I love it so much but I do. Hundreds of little maneki-neko statues donated by visitors over generations. It's quiet, it's beautiful, and it's completely unlike anywhere else in the city.", 4.6),
    ("Tokyo", "YAYOI KUSAMA Museum", "Places to See", "The Kusama Museum is one of the most moving art experiences in Tokyo for me. Small, intimate, and her works feel completely different when you're surrounded by them. Book well in advance because it always sells out.", 4.0),
    ("Tokyo", "Sushi Yuu", "Food", "Sushi Yuu is extraordinary. You sit at the counter, you trust the chef, and something really special unfolds piece by piece. The precision and the quality are unlike almost anything I've experienced. One of the best sushi meals I've had anywhere in the world.", 4.8),
    ("Prishtina", "National Gallery of Kosovo", "Places to See", "The National Gallery is an important institution to us, featuring all kinds of Albanian and Kosovar art. It draws me back every single trip.", 4.8),
    ("Prishtina", "Old Green Market", "Places to See", "The Old Green Market is where Prishtina's daily life happens. Fresh produce, local spices, vendors who have been there for decades. It's the best way to understand the city if you're visiting for the first time.", 4.2),
    ("Prishtina", "Libraria Dukagjini", "Places to See", "Dukagjini is the oldest bookshop in Prishtina. It means a lot to a lot of people because it's a statement about culture and continuity. I always find something in Albanian I haven't read yet and take it home.", 4.7),
    ("Prishtina", "Servis Fantazia", "Nightlife", "Servis Fantazia has a really amazing, specific energy. It's been described as the most diverse place in Prishtina and when you walk in you feel that immediately. Everyone is welcome and everyone knows it.", 4.7),
    ("Prishtina", "Churchill", "Nightlife", "Churchill is the kind of bar you need in the middle of a long Prishtina night out. It's been there for years and it knows just what it is. Reliable, always filled with people.", 4.8),
    ("Prishtina", "Monròe", "Nightlife", "Monroe has the best bar energy in the city. It builds slowly over the evening and then suddenly the whole night is right there. Good music, good crowd, good drinks. Go late.", 4.4),
    ("Prishtina", "Basilico", "Food", "Basilico is my go-to when I want Italian in Prishtina, and I know that sounds like a strange thing to say but it's just really good. Consistent, warm, and the pasta is made properly. A real neighbourhood restaurant.", 4.5),
    ("Prishtina", "Tiffany", "Food", "Tiffany in Prishtina is the most homey restaurant in the middle of the city. Being away so much I don't really get to eat traditional Albanian food as much as I'd like. So I come here to get my fix.", 4.3),
    ("Tirana", "Salt Tirana", "Food", "Salt Tirana is a great choice when you want to eat really well without any fuss. The Albanian flavours are there, and everything feels a little elevated. I always leave happy.", 4.5),
    ("Tirana", "Soma Slow Food", "Food", "The food at Soma Slow Food is what I love. Everything feels like it came from somewhere close and was made with genuine care. Simple, honest cooking.", 4.2),
    ("Tirana", "Soma Book Station", "Food", "Soma is one of my favourite places in the city. It's a bookshop but it's also a gathering point, a coffee spot, a community space.", 4.5),
    ("New York City", "Treasures of NYC", "Places to See", "Treasures of NYC is a vintage resale shop that takes its mandate seriously. The pieces are real, the prices are fair, and the selection turns over constantly. You'll find things there that you won't find anywhere else.", 5.0),
    ("New York City", "Corner Bistro", "Food", "Corner Bistro is wholly the experience of having their iconic burger in the bar that has looked exactly the same since 1961. That is New York to me.", 4.3),
    ("New York City", "Angelika Film Center", "Places to See", "The Angelika is where I go when I want to see something I wouldn't know to look for. It's been there since 1989 and it still programmes with real taste and variety.", 4.4),
    ("New York City", "Cherry Lane Theatre", "Places to See", "I just love going to Cherry Lane Theatre, which is sort of hidden down a backlane in the West Village. It's New York's oldest Off-Broadway Theater and known as \"The Birthplace of Off-Broadway.\" There's always something provocative playing and the talent blows me away every time.", 4.7),
    ("New York City", "Bridges", "Food", "Bridges is one of the more exciting new-ish openings in New York right now. The cooking is smart, the room is beautiful, and it already has the feeling of somewhere that's going to last.", 4.5),
    ("New York City", "Bar Oliver", "Nightlife", "Bar Oliver is the kind of Spanish wine bar that feels like it flew in directly from Madrid. Small plates, really good pours by the glass, and the atmosphere builds as the night goes on. A go-to.", 4.4),
    ("New York City", "Thai Diner", "Food", "Thai Diner is from the team behind Michelin-starred Uncle Boons. The cooking is bold and specific, the drinks list is creative, and it's a diner in the best sense of that word. Nothing feels gimmicky -- it's just excellent food.", 4.4),
    ("New York City", "Raf's", "Food", "Raf's is doing something that feels new with French cafe culture. The pastries are incredible, the natural wine list is thoughtful, and the way the room feels at lunch is just right.", 4.1),
    ("New York City", "I Sodi", "Food", "I Sodi in the West Village is where I go when I want to feel like I live in New York. Florentine cooking, great Chianti, candlelight. It has the feeling of a place that has been there forever.", 4.2),
    ("New York City", "Manjul Coffee & Clothing", "Food", "Manjul is a tiny, focused coffee shop that does everything the way I like it. Really good beans, careful brewing, never too loud or crowded. A perfect start to any New York morning.", 4.5),
    ("Los Angeles", "Skylight Books", "Places to See", "Skylight Books in Los Feliz is my favourite kind of indie bookshop. Genuinely curated, the staff have read everything, and the window displays are always exceptional. I never leave without at least three books that found me versus the other way around.", 4.7),
    ("Los Angeles", "Remedy Place West Hollywood", "Places to See", "Remedy Place is my recovery spot in LA. Infrared sauna, cold plunge, the whole package. It's the kind of wellness that makes me feel like my cells are regenerating. I always sleep so much better afterwards.", 4.9),
    ("Los Angeles", "Runyon Canyon Park", "Places to See", "Hike from the trails in Runyon Canyon Park to Griffith Observatory, enjoy the art and architecture up there, and remember why LA is loved for its lifestyle.", 4.8),
    ("Los Angeles", "Sunset Tower Hotel", "Places to Stay", "Sunset Tower is old Hollywood in the most beautiful way. Have a drink at the bar in the late afternoon and watch the light change over the city.", 4.6),
    ("Los Angeles", "New Beverly Cinema", "Places to See", "The New Beverly is Quentin Tarantino's cinema and it only screens 35mm film. The programming is cinephile-level and you'll see something you wouldn't find elsewhere. It feels like a secret even though everyone in LA knows about it.", 4.8),
    ("Los Angeles", "The Broad", "Places to See", "The Broad is free to visit and it has one of the best permanent contemporary art collections in the city. Jeff Koons, Kara Walker, Cindy Sherman. I always leave moved, so much so it's worth building a whole afternoon around.", 4.7),
    ("Los Angeles", "Cookbook Market & Cafe - Larchmont", "Food", "Cookbook is this incredible market-cafe on Larchmont that I keep coming back to every time I'm in LA. The kind of place where you pick up great cheese and wine and end up creating an evening around ingredients you didn't know you needed.", 3.7),
    ("Los Angeles", "Found Oyster", "Food", "Found Oyster is exactly what it sounds like and I mean that in the best possible way. Fresh oysters, good wine. Sometimes that's all you need and Found Oyster totally understands that.", 4.6),
    ("Los Angeles", "Anajak Thai Cuisine", "Food", "Anajak Thai is a family-run spot in Sherman Oaks that has become something really special. They do natural wine pairings with traditional Thai cooking, which sounds unusual but makes complete sense once you're sitting there.", 4.1),
    ("Los Angeles", "Go's Mart", "Food", "Go's Mart is quietly famous for their Omakase that is both hit after hit of the classics, plus unexpected and modern delights that I don't think any other Sushi restaurant can match. A very unassuming sushi spot that's worth the trip deep into the Valley for some of the best omakase LA has to offer.", 4.6),
    ("Los Angeles", "Damian", "Food", "Damian is doing some of the most exciting Mexican cooking outside of Mexico. It's in a beautiful space downtown and the approach to seafood and coastal flavours is exceptional. Don't skip the aguachile.", 4.5),
    ("London", "The Hero - Maida Vale", "Nightlife", "Sometimes what you want is a really good pub and The Hero is exactly that. Easy drinks, warm atmosphere, and you feel welcomed the moment you walk in. An honest neighbourhood spot.", 4.3),
    ("London", "Lore of the Land", "Nightlife", "This pub is three floors of dark wood, eclectic art, and the kind of atmosphere that makes you want to cancel your plans and stay all afternoon. The Sunday roast is the reason to book ahead -- with venison and the Lore doughnut as non-negotiables, everything cooked over a bespoke charcoal oven and washed down with something from their own brewery.", 4.6),
    ("London", "Canteen | Notting Hill", "Food", "Canteen is one of my favourite new spots. It's proper cooking: no nonsense, just delicious! I love the variety of pastas and risottos, it's all locally sourced. I love the simplicity of their cocktails -- they do a great negroni. And that chocolate mousse. Even when you're full, out comes the second stomach.", None),
    ("London", "Levan Restaurant Peckham", "Food", "Levan in Peckham makes you feel lucky to be in London. Great natural wine, beautiful small plates.", None),
    ("London", "Fonda", "Food", "Fonda is excellent Mexican in London. Chef Santiago Lastra really understands flavour. The tlayudas, the mezcal list, all of it has made it a real favourite.", None),
    ("London", "Trullo", "Food", "Trullo is what pasta should feel like. A neighbourhood Italian in Highbury that doesn't try too hard, and is consistently brilliant. The hand rolled pappardelle is worth making the reservation.", None),
    ("London", "Westerns Laundry", "Food", "Westerns Laundry is a former prison laundrette turned into a Michelin Bib Gourmand seafood restaurant -- Primeur, its sister restaurant, is a few minutes walk away in a former garage that still has the original Barnes Motors sign above the door.", None),
    ("London", "Berenjak Soho", "Food", "It takes what people would normally think of as street food and makes it a whole experience. When people think of Persian food they think of Kebabs but Berenjak is changing that.", None),
    ("London", "The Quality Chop House", "Food", "Quality Chop House has been around since 1869 and it still feels relevant. The confit potatoes are iconic and the wine list is one of the best in London. Go for a long, slow lunch.", 4.6),
    ("London", "BRAT Restaurant", "Food", "I love the food, love the vibe, never lets me down.", 4.5),
    ("London", "Ida", "Food", "Ida is just such an Italian family run restaurant. It's quaint, warm, and unassuming. It's down this little residential street. It makes me feel fuzzy inside.", 4.5),
    ("London", "Mountain Beak Street", "Food", "Mountain is the place I go when I want small plates, locally sourced. It just never disappoints. I always leave happy.", 4.4),
]

# New cities that don't yet exist in the file
NEW_CITIES = {
    "Antwerp": {
        "country": "Belgium", "emoji": "🇧🇪",
        "tagline": "🍫 A diamond-cut Flemish port city of medieval guild houses, fashion provocateurs, and Rubens — quieter than Brussels but with twice the style.",
        "coords": [51.2194, 4.4025], "region": "Europe",
    },
    "Austin": {
        "country": "USA", "emoji": "🇺🇸",
        "tagline": "🎸 Texas's live music capital — honky-tonks, breakfast tacos, swimming holes, and a creative community keeping it weird.",
        "coords": [30.2672, -97.7431], "region": "North America",
    },
    "Bangkok": {
        "country": "Thailand", "emoji": "🇹🇭",
        "tagline": "🛺 A megacity of contradictions — gilded temples beside neon sois, Michelin-starred street stalls, all-night markets, and some of the world's most generous hospitality.",
        "coords": [13.7563, 100.5018], "region": "Asia",
    },
    "Brussels": {
        "country": "Belgium", "emoji": "🇧🇪",
        "tagline": "🍺 The capital of comic strips, frites, and weird-good beer — a polyglot European hub that hides genuine charm in its courtyards and corner cafés.",
        "coords": [50.8503, 4.3517], "region": "Europe",
    },
    "Cornwall": {
        "country": "UK", "emoji": "🇬🇧",
        "tagline": "🌊 England's Atlantic edge — wild cliffs, fishing harbours, surf beaches and the country's best seafood. A different rhythm entirely.",
        "coords": [50.2660, -5.0527], "region": "Europe",
    },
    "Hong Kong": {
        "country": "Hong Kong", "emoji": "🇭🇰",
        "tagline": "🏙️ Vertical city of dim sum trolleys and dai pai dongs, neon-lit alleys and ferry rides across the harbour. Eat constantly, move constantly.",
        "coords": [22.3193, 114.1694], "region": "Asia",
    },
    "Kuala Lumpur": {
        "country": "Malaysia", "emoji": "🇲🇾",
        "tagline": "🌴 Malay, Chinese, and Indian cultures layered into a tropical capital — hawker stalls, jungle on the horizon, and a young creative scene quietly making waves.",
        "coords": [3.1390, 101.6869], "region": "Asia",
    },
    "Marseille": {
        "country": "France", "emoji": "🇫🇷",
        "tagline": "⚓ France's salty, sun-baked Mediterranean capital — bouillabaisse, calanques, hip-hop and pastis. A city with grit and grace in equal measure.",
        "coords": [43.2965, 5.3698], "region": "Europe",
    },
    "Nashville": {
        "country": "USA", "emoji": "🇺🇸",
        "tagline": "🎤 Music City — honky-tonks on Broadway, hot chicken, songwriter rounds in dive bars, and a Southern hospitality you can feel the moment you arrive.",
        "coords": [36.1627, -86.7816], "region": "North America",
    },
    "Prishtina": {
        "country": "Kosovo", "emoji": "🇽🇰",
        "tagline": "☕ Europe's youngest capital — fierce coffee culture, a fast-growing arts scene, and a hospitality that comes from a country still defining itself.",
        "coords": [42.6629, 21.1655], "region": "Europe",
    },
    "Tirana": {
        "country": "Albania", "emoji": "🇦🇱",
        "tagline": "🎨 A capital that has reinvented itself in colour — Soviet-era blocks painted vivid, sprawling cafés, leafy boulevards, and food that surprises every visitor.",
        "coords": [41.3275, 19.8187], "region": "Europe",
    },
    "Singapore": {
        "country": "Singapore", "emoji": "🇸🇬",
        "tagline": "🥢 Hawker centres are temples here — chicken rice, laksa, chilli crab. A city-state that takes both food and design extremely seriously.",
        "coords": [1.3521, 103.8198], "region": "Asia",
    },
}

# Country code additions (flagcdn)
NEW_CCODES = {
    "Belgium": "be", "Thailand": "th", "Hong Kong": "hk", "Malaysia": "my",
    "Kosovo": "xk", "Singapore": "sg",
}

# ─── Read file ────────────────────────────────────────────────────────────────
html = HTML_PATH.read_text(encoding='utf-8')

def extract_object(text, marker):
    """Find `marker` in text and return (start_of_object_brace, end_of_matching_brace+1)."""
    i = text.find(marker)
    assert i >= 0, f"{marker!r} not found"
    obj_start = text.find('{', i)
    depth = 0
    in_str = False
    esc = False
    for j in range(obj_start, len(text)):
        ch = text[j]
        if in_str:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == '"': in_str = False
        else:
            if ch == '"': in_str = True
            elif ch == '{': depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return obj_start, j + 1
    raise ValueError(f"unbalanced braces after {marker!r}")

def replace_object(text, marker, new_json):
    s, e = extract_object(text, marker)
    return text[:s] + new_json + text[e:]

# ─── 1. Update PLACES ─────────────────────────────────────────────────────────
ps, pe = extract_object(html, "const PLACES=")
places = json.loads(html[ps:pe])

def maps_url(name, city):
    q = urllib.parse.quote_plus(f"{name} {city}")
    return f"https://www.google.com/maps/search/?api=1&query={q}"

added_count = 0
for city, name, cat, desc, rating in PLACES_DATA:
    entry = {"n": name, "c": cat, "d": desc, "u": maps_url(name, city), "dl": True}
    if rating is not None:
        entry["r"] = rating
    places.setdefault(city, []).append(entry)
    added_count += 1

# Sort each city's places alphabetically by name (matches existing convention)
for k in places:
    places[k].sort(key=lambda p: p["n"].lower())

html = replace_object(html, "const PLACES=", json.dumps(places, ensure_ascii=False, separators=(',', ':')))
print(f"PLACES: added {added_count} entries")

# ─── 2. Update META ───────────────────────────────────────────────────────────
ms, me = extract_object(html, "const META=")
meta = json.loads(html[ms:me])
new_meta_count = 0
for city, info in NEW_CITIES.items():
    if city not in meta:
        meta[city] = {"country": info["country"], "emoji": info["emoji"], "tagline": info["tagline"]}
        new_meta_count += 1
html = replace_object(html, "const META=", json.dumps(meta, ensure_ascii=False, separators=(',', ':')))
print(f"META: added {new_meta_count} entries (now {len(meta)} cities)")

# ─── 3. Update COORDS ─────────────────────────────────────────────────────────
coords_start, coords_end = extract_object(html, "const COORDS=")
coords_block = html[coords_start:coords_end]
for city, info in NEW_CITIES.items():
    if f"'{city}':" in coords_block or f'"{city}":' in coords_block:
        continue
    lat, lng = info["coords"]
    entry = f"'{city}':[{lat},{lng}],"
    # Insert right after `const COORDS={` (which is just before coords_start+1)
    html = html.replace("const COORDS={", "const COORDS={" + entry, 1)
print("COORDS: inserted new cities")

# ─── 4. Update REGIONS ────────────────────────────────────────────────────────
for city, info in NEW_CITIES.items():
    region = info["region"]
    # Find region line and check if city already in it
    pat = re.compile(r"('" + re.escape(region) + r"':\s*\[)([^\]]+)(\])")
    m = pat.search(html)
    assert m, f"Region {region} not found"
    inner = m.group(2)
    if f"'{city}'" in inner:
        continue
    # Insert alphabetically: append at end (sort happens in JS render? actually it doesn't, but order doesn't matter much)
    # Insert in alphabetical order by parsing and re-emitting
    items = [s.strip().strip("'") for s in inner.split(",") if s.strip()]
    items.append(city)
    items.sort(key=str.lower)
    new_inner = ", ".join(f"'{c}'" for c in items)
    html = pat.sub(lambda _m: _m.group(1) + new_inner + _m.group(3), html, count=1)
print("REGIONS: inserted new cities")

# ─── 5. Update CCODES ─────────────────────────────────────────────────────────
cs, ce = extract_object(html, "const CCODES=")
ccodes = json.loads(html[cs:ce])
for country, code in NEW_CCODES.items():
    if country not in ccodes:
        ccodes[country] = code
html = replace_object(html, "const CCODES=", json.dumps(ccodes, ensure_ascii=False, separators=(', ', ': ')))
print("CCODES: inserted new country codes")

# ─── 6. Patch JS for Dua Lipa tab ────────────────────────────────────────────
# 6a. tabSlug — add dua-lipa
old_tabSlug = "function tabSlug(k){return k==='All'?'':k==='My Favorites'?'favorites':slug(k);}"
new_tabSlug = "function tabSlug(k){return k==='All'?'':k==='My Favorites'?'favorites':k===\"Dua Lipa's Favorites\"?'dua-lipa':slug(k);}"
assert old_tabSlug in html, "tabSlug not found"
html = html.replace(old_tabSlug, new_tabSlug, 1)

# 6b. tabFromSlug
old_tabFromSlug = "function tabFromSlug(s,cats){if(!s||s==='all')return 'All';if(s==='favorites')return 'My Favorites';return cats.find(c=>slug(c)===s)||'All';}"
new_tabFromSlug = "function tabFromSlug(s,cats){if(!s||s==='all')return 'All';if(s==='favorites')return 'My Favorites';if(s==='dua-lipa')return \"Dua Lipa's Favorites\";return cats.find(c=>slug(c)===s)||'All';}"
assert old_tabFromSlug in html, "tabFromSlug not found"
html = html.replace(old_tabFromSlug, new_tabFromSlug, 1)

# 6c. buildTabs — inject Dua Lipa tab after My Favorites
old_buildTabs = """function buildTabs(cats){
  const pl=PLACES[city]||[];
  const allN=pl.length;
  const favN=pl.filter(p=>p.f).length;
  const allTab=`<div class="tab${'All'===cat?' on':''}" onclick="selCat('All')">All <span style="color:var(--ink-muted);margin-left:2px">${allN}</span></div>`;
  const favTab=favN?`<div class="tab${'My Favorites'===cat?' on':''}" onclick="selCat('My Favorites')">My Favorites <span style="color:var(--ink-muted);margin-left:2px">${favN}</span></div>`:'';
  document.getElementById('tabs').innerHTML=allTab+favTab+cats.map(k=>{
    const n=pl.filter(p=>p.c===k).length;
    return `<div class="tab${k===cat?' on':''}" onclick="selCat('${k.replace(/'/g,"\\'")}')"> ${k} <span style="color:var(--ink-muted);margin-left:2px">${n}</span></div>`;
  }).join('');
}"""
new_buildTabs = """function buildTabs(cats){
  const pl=PLACES[city]||[];
  const allN=pl.length;
  const favN=pl.filter(p=>p.f).length;
  const dlN=pl.filter(p=>p.dl).length;
  const allTab=`<div class="tab${'All'===cat?' on':''}" onclick="selCat('All')">All <span style="color:var(--ink-muted);margin-left:2px">${allN}</span></div>`;
  const favTab=favN?`<div class="tab${'My Favorites'===cat?' on':''}" onclick="selCat('My Favorites')">My Favorites <span style="color:var(--ink-muted);margin-left:2px">${favN}</span></div>`:'';
  const dlTab=dlN?`<div class="tab dl-tab${\"Dua Lipa's Favorites\"===cat?' on':''}" onclick=\"selCat(&quot;Dua Lipa's Favorites&quot;)\">Dua Lipa's Favorites <span style=\"color:var(--ink-muted);margin-left:2px\">${dlN}</span></div>`:'';
  document.getElementById('tabs').innerHTML=allTab+favTab+dlTab+cats.map(k=>{
    const n=pl.filter(p=>p.c===k).length;
    return `<div class="tab${k===cat?' on':''}" onclick="selCat('${k.replace(/'/g,"\\'")}')"> ${k} <span style="color:var(--ink-muted);margin-left:2px">${n}</span></div>`;
  }).join('');
}"""
assert old_buildTabs in html, "buildTabs not found"
html = html.replace(old_buildTabs, new_buildTabs, 1)

# 6d. renderPlaces filter — add dl branch
old_filter = "const places=k==='All'?all:k==='My Favorites'?all.filter(p=>p.f):all.filter(p=>p.c===k);"
new_filter = "const places=k==='All'?all:k==='My Favorites'?all.filter(p=>p.f):k===\"Dua Lipa's Favorites\"?all.filter(p=>p.dl):all.filter(p=>p.c===k);"
assert old_filter in html, "filter not found"
html = html.replace(old_filter, new_filter, 1)

# 6e. Inline badge in list rendering — show DL badge alongside fave badge
old_badge = "const fav=(p.f&&k!=='My Favorites')?'<span class=\"fave-badge-inline\">♥</span>':'';"
new_badge = ("const fav=(p.f&&k!=='My Favorites')?'<span class=\"fave-badge-inline\">♥</span>':'';\n"
             "    const dlBadge=(p.dl&&k!==\"Dua Lipa's Favorites\")?'<span class=\"dl-badge-inline\" title=\"Dua Lipa\\'s favorite\">DL</span>':'';")
assert old_badge in html, "fav badge line not found"
html = html.replace(old_badge, new_badge, 1)
# Inject the dlBadge into the meta row
old_meta_html = "<div class=\"pli-meta\"><span class=\"ppill\">${pill}</span>${fav}</div>"
new_meta_html = "<div class=\"pli-meta\"><span class=\"ppill\">${pill}</span>${fav}${dlBadge}</div>"
assert old_meta_html in html, "pli-meta row not found"
html = html.replace(old_meta_html, new_meta_html, 1)

# 6f. Modal review styling — show as review when dl:true (similar to f:true)
old_modal_branch = "if(p.d&&p.f===true){"
new_modal_branch = "if(p.d&&(p.f===true||p.dl===true)){"
assert old_modal_branch in html, "modal review branch not found"
html = html.replace(old_modal_branch, new_modal_branch, 1)

# Add a subtitle in modal when dl tag is set
old_mcity_line = "document.getElementById('mCity').textContent=c+' · '+(META[c]?.country||'');"
new_mcity_line = ("document.getElementById('mCity').textContent=c+' · '+(META[c]?.country||'')+(p.dl?\" · Dua Lipa's Favorite\":'');")
assert old_mcity_line in html, "mCity line not found"
html = html.replace(old_mcity_line, new_mcity_line, 1)

# 6g. Add CSS for the DL badge — insert near .fave-badge-inline rule
old_css_anchor = ".fave-badge-inline{color:#e87040;font-size:12px;}"
new_css_block = (".fave-badge-inline{color:#e87040;font-size:12px;}"
                 ".dl-badge-inline{display:inline-flex;align-items:center;justify-content:center;background:#4a7fe8;color:#fff;font-size:9px;font-weight:700;letter-spacing:0.08em;padding:2px 6px;border-radius:2px;line-height:1;}"
                 ".dl-tab{position:relative;}.dl-tab::before{content:'';display:inline-block;width:6px;height:6px;border-radius:50%;background:#4a7fe8;margin-right:7px;vertical-align:middle;}")
assert old_css_anchor in html, "CSS anchor not found"
html = html.replace(old_css_anchor, new_css_block, 1)

# ─── Write ────────────────────────────────────────────────────────────────────
HTML_PATH.write_text(html, encoding='utf-8')
print(f"\nDone. {added_count} Dua Lipa places added, {len(NEW_CITIES)} new cities.")
