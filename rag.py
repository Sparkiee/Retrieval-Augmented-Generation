import spacy

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")

text = "I want to purchase a new car, a Hyundai 2012 and not a Tesla and not a Toyota or Volvo, I want the car to be EV aswell. I'm looking for a price more than 20,000$ but less than 30,000$, around 25,000$ please no petrol"
doc = nlp(text)

car_brands = [
    "Abarth",
    "Alfa Romeo",
    "Aston Martin",
    "Audi",
    "Bentley",
    "BMW",
    "Bugatti",
    "Cadillac",
    "Chevrolet",
    "Chrysler",
    "Citroën",
    "Dacia",
    "Daewoo",
    "Daihatsu",
    "Dodge",
    "Donkervoort",
    "DS",
    "Ferrari",
    "Fiat",
    "Fisker",
    "Ford",
    "Honda",
    "Hummer",
    "Hyundai",
    "Infiniti",
    "Iveco",
    "Jaguar",
    "Jeep",
    "Kia",
    "KTM",
    "Lada",
    "Lamborghini",
    "Lancia",
    "Land Rover",
    "Landwind",
    "Lexus",
    "Lotus",
    "Maserati",
    "Maybach",
    "Mazda",
    "McLaren",
    "Mercedes-Benz",
    "Mercedes",
    "MG",
    "Mini",
    "Mitsubishi",
    "Morgan",
    "Nissan",
    "Opel",
    "Peugeot",
    "Porsche",
    "Renault",
    "Rolls-Royce",
    "Rover",
    "Saab",
    "Seat",
    "Skoda",
    "Smart",
    "SsangYong",
    "Subaru",
    "Suzuki",
    "Tesla",
    "Toyota",
    "Volkswagen",
    "Volvo",
]

vehicle_types = [
    "SUV",
    "Sedan",
    "Coupe",
    "Convertible",
    "Hatchback",
    "Wagon",
    "Van",
    "Truck",
    "Minivan",
    "Pickup",
    "Crossover",
    "Roadster",
    "Limousine",
    "Cabriolet",
    "Targa",
    "MPV",
    "Compact",
    "Subcompact",
    "Full-size",
    "Mid-size",
    "Micro",
    "Mini",
    "Supermini",
    "Compact executive",
    "Executive",
    "Luxury",
    "Sports",
    "Supercar",
    "Muscle",
    "Pony",
    "Pony car",
    "Pony car",
    "Hot hatch",
    "Kei car",
    "City car",
    "Economy car",
    "Family car",
    "Grand tourer",
    "Grand tourer",
    "Compact MPV",
    "Mini MPV",
    "Large MPV",
    "Crossover SUV",
    "Mini SUV",
    "Compact SUV",
    "Mid-size SUV",
    "Full-size SUV",
    "Extended-length SUV",
    "Off-roader",
    "Off-road vehicle",
    "Sport utility truck",
    "Sport utility truck",
    "Sport utility vehicle",
    "Sport utility vehicle",
    "Compact pickup truck",
    "Mid-size pickup truck",
    "Full-size pickup truck",
    "Compact van",
]

fuel_types = ["Petrol", "Diesel", "Electric", "Hybrid", "EV", "PULP 95"]

categories = ["BRAND", "PRICE", "MODEL"]

greater = ["above", "more than", "greater than", "higher than", "over", "exceeding"]
lesser = ["below", "less than", "lower than", "under", "beneath", "not exceeding"]
equal = [
    "equal to",
    "same as",
    "equal",
    "same",
    "around",
    "approximately",
    "about",
    "near",
    "nearly",
    "close to",
    "just over",
    "just under",
    "just above",
    "just below",
]
connectors = [
    "and",
    "or",
    "but",
    "nor",
    "yet",
    "so",
    "for",
    "because",
    "although",
    "since",
    "unless",
    "while",
    "whereas",
    "where",
    "wherever",
    "when",
    "whenever",
    "whether",
    "which",
    "who",
    "whoever",
    "whom",
    "whose",
    "that",
    "what",
    "whatever",
    "which",
    "whichever",
    "whomsoever",
    "whosoever",
    "how",
    "however",
    "why",
    "either",
]
negation = ["not", "no", "without", "exclude", "excluding"]

query_information = {
    "brand": None,
    "model": None,
    "production_year": None,
    "price_min": None,
    "price_max": None,
    "price_avg": None,
    "excluded_brands": [],
    "fuel_type": None,
    "excluded_fuel_types": [],
}

# looping through the sentences in the query
for sent in doc.sents:
    # looping through the tokens in the sentence
    for token in sent:
        # if we encounter a negation word
        if token.text.lower() in negation:
            # get the following context of the negation word
            context = doc[token.i : min(len(doc), token.i + 5)].text.lower()
            # check if the context contains any car brands or fuel types, we exclude them from the query
            for brand in car_brands:
                if brand.lower() in context:
                    query_information["excluded_brands"].append(brand)
            for fuel in fuel_types:
                if fuel.lower() in context:
                    query_information["excluded_fuel_types"].append(fuel)

        # brand detection
        if token.text.lower() in [brand.lower() for brand in car_brands]:
            if token.text.lower() not in [
                excluded.lower() for excluded in query_information["excluded_brands"]
            ]:
                query_information["brand"] = token.text
                next_token = token.nbor()  # get the next token
                if next_token.is_alpha or (
                    not next_token.is_alpha and not next_token.like_num
                ):  # if the next token is an alphanumeric like 'i20'
                    query_information["model"] = next_token.text

                    if next_token.nbor().like_num and len(next_token.nbor().text) == 4:
                        query_information["production_year"] = next_token.nbor().text
                elif next_token.like_num and len(next_token.text) == 4:
                    query_information["production_year"] = next_token.text
                else:
                    query_information["model"] = None

        # fuel type detection
        if token.text.lower() in [
            fuel.lower() for fuel in fuel_types
        ] and token.text.lower() not in [
            excluded.lower() for excluded in query_information["excluded_fuel_types"]
        ]:
            query_information["fuel_type"] = token.text

        # if the token is a number, we check the context to see if it is a price, or a range and assign it to the query_information
        if token.like_num:
            context = doc[max(0, token.i - 5) : token.i].text.lower()
            for keyword in greater:
                if keyword in context:
                    query_information["price_min"] = token.text
            for keyword in lesser:
                if keyword in context:
                    query_information["price_max"] = token.text
            for keyword in equal:
                if keyword in context:
                    query_information["price_avg"] = token.text

print("Query: ", text)
print("Query Information", query_information)
