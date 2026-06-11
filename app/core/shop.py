from app.data.default_items import DEFAULT_ITEMS


class Shop:
    def __init__(self):
        self.items = DEFAULT_ITEMS

    def list_items(self):
        return self.items

    def buy_item(self, party, pet, item_index):
        """Compra um item usando as moedas globais da PetParty.

        O dinheiro do jogador fica em PetParty.money, não no Pet.
        Retorna (sucesso, mensagem) para a UI decidir como mostrar o resultado.
        """
        if item_index < 0 or item_index >= len(self.items):
            return False, "Item inválido."

        item = self.items[item_index]

        if party.money < item.price:
            return False, "Moedas insuficientes."

        party.money -= item.price
        pet.inventory.append(item.name)

        return True, f"{pet.name} comprou {item.name}."

    def get_item_by_name(self, item_name):
        for item in self.items:
            if item.name == item_name:
                return item

        return None
