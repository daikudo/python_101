import random

alcohol = [
    "Денатурат (технический спирт) – 100 г.",
    "Бархатное пиво – 200 г.",
    "Пиво «Жигулевское» – 100 г.",
    "Водка",
    "Розовое крепкое вино",
]

technical = [
    "Политура очищенная – 100 г.",
    "Духи «Белая сирень» – 50 г.",
    "Лак спиртовой – 150 г.",
    "Средство от потливости ног – 50 г.",
    "Лак для ногтей – 2 г.",
    "Зубной эликсир – 150 г.",
    "Шампунь «Садко – богатый гость» – 30 г.",
    "Резоль для очистки волос от перхоти – 70 г.",
    "Дезинсектакль для уничтожения мелких насекомых – 20 г.",
]

aromatic = [
    "Лаванда – 15 г.",
    "Вербена – 15 г.",
    "«Лесная вода» – 30 г.",
    "Лимонад – 150 г.",
]

methods = [
    "Смешать до однородной консистенции черно-бурого цвета.",
    "Смешать, но не взбалтывать.",
    "Приготовляемую смесь двадцать минут помешивать веткой жимолости (повиликой — нельзя).",
    "Смешать в любой пропорции.",
    "Настаивать в течение недели на табаке сигарных сортов.",
]


def generate_cocktail():
    chosen_alcohol = random.choice(alcohol)
    chosen_technical = random.sample(technical, 2)
    chosen_aromatic = random.choice(aromatic)
    chosen_method = random.choice(methods)

    ingredients = [chosen_alcohol] + chosen_technical + [chosen_aromatic]
    return ingredients, chosen_method


if __name__ == "__main__":
    ingredients, method = generate_cocktail()

    print("Ингредиенты:")
    for item in ingredients:
        print(f"- {item}")
    print("\nСпособ приготовления:")
    print(method)