import spacy
import re
import mysql.connector


class QueryParser:
    def __init__(self, text):
        self.text = text
        self.nlp = spacy.load("en_core_web_sm")
        self.doc = self.nlp(text)
        self.car_brands = [
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
        self.fuel_types = ["Petrol", "Diesel", "Electric", "Hybrid", "EV", "PULP 95"]
        self.negation = ["not", "no", "without", "exclude", "excluding"]
        self.greater = [
            "above",
            "more than",
            "greater than",
            "higher than",
            "over",
            "exceeding",
        ]
        self.lesser = [
            "below",
            "less than",
            "lower than",
            "under",
            "beneath",
            "not exceeding",
        ]
        self.equal = [
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
        self.query_information = {
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
        self.money_signs = ["$", "€", "£", "₪"]
        self.money_names = ["dollar", "euro", "pound", "shekel"]
        self.parse_query()

    def parse_query(self):

        # combo_options = [re.escape(m) for m in self.money_signs] + [
        #     " " + m for m in self.money_names
        # ]
        # pattern = r"\d{1,3}(?:,\d{3})*\s?(?:" + "|".join(combo_options) + r")"
        # matches = re.findall(pattern, self.text)

        for sent in self.doc.sents:
            for token in sent:
                if token.text.lower() in self.negation:
                    context = self.doc[
                        token.i : min(len(self.doc), token.i + 5)
                    ].text.lower()
                    for brand in self.car_brands:
                        if brand.lower() in context:
                            self.query_information["excluded_brands"].append(brand)
                    for fuel in self.fuel_types:
                        if fuel.lower() in context:
                            self.query_information["excluded_fuel_types"].append(fuel)

                if token.text.lower() in [brand.lower() for brand in self.car_brands]:
                    if token.text.lower() not in [
                        excluded.lower()
                        for excluded in self.query_information["excluded_brands"]
                    ]:
                        self.query_information["brand"] = token.text
                        next_token = token.nbor()
                        if next_token.is_alpha or (
                            not next_token.is_alpha and not next_token.like_num
                        ):
                            self.query_information["model"] = next_token.text
                            if (
                                next_token.nbor().like_num
                                and len(next_token.nbor().text) == 4
                            ):
                                self.query_information["production_year"] = (
                                    next_token.nbor().text
                                )
                        elif next_token.like_num and len(next_token.text) == 4:
                            self.query_information["production_year"] = next_token.text
                        else:
                            self.query_information["model"] = None

                if token.text.lower() in [
                    fuel.lower() for fuel in self.fuel_types
                ] and token.text.lower() not in [
                    excluded.lower()
                    for excluded in self.query_information["excluded_fuel_types"]
                ]:
                    self.query_information["fuel_type"] = token.text

                if token.like_num:
                    context = self.doc[max(0, token.i - 5) : token.i].text.lower()
                    for keyword in self.greater:
                        if keyword in context:
                            self.query_information["price_min"] = token.text
                    for keyword in self.lesser:
                        if keyword in context:
                            self.query_information["price_max"] = token.text
                    for keyword in self.equal:
                        if keyword in context:
                            self.query_information["price_avg"] = token.text

    def get_query_information(self):
        return self.query_information


# Example usage
text = "I want to purchase a new car, a Hyundai 2012 and not a Tesla and not a Toyota or Volvo, I want the car to be EV aswell. I'm looking for a price more than 20,000$ but less than 30,000$, around 25,000$ please no petrol"
parser = QueryParser(text)
print("Query: ", text)
print("Query Information", parser.get_query_information())
