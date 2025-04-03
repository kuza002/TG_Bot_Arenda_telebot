class Ad:
    ALL_DISTRICTS = [
        "Вареничная Слобода", "Беспонтово", "Громкодумье", "Мямлино", "Безалаберск",
        "Пельменёво", "Котлетный Рай", "Колбасные Кварталы", "Блинопухово", "Мурлыкино", "Бултых-Поволжский"
    ]

    def __init__(self, user_id,district, price, address):
        self.user_id = user_id
        self.district = district
        self.price = price
        self.address = address