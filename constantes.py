import discord
import json
from discord import app_commands

class ConstantesGP(app_commands.Group):
	def __init__(self):
		super().__init__(description="Comandos das constantes do Bot")
	
	class EditValueModal(discord.ui.Modal, title="Editar valor"):
		def __init__(self, config, save_func, categoria, item):
			super().__init__()
			self.config = config
			self.save_func = save_func
			self.categoria = categoria
			self.item = item

			valor_atual = str(config[categoria][item])

			self.add_item(discord.ui.TextInput(
				label=f"Novo valor para {item}:",
				placeholder=valor_atual,
				default=valor_atual,
				max_length=100
			))

		async def on_submit(self, interaction: discord.Interaction):
			novo_valor = self.children[0].value

			self.config[self.categoria][self.item] = novo_valor
			self.save_func()

			await interaction.response.send_message(f"✅ Valor de `{self.item}` atualizado para `{novo_valor}`.", ephemeral=True)

	class SetupView(discord.ui.View):
		def __init__(self, config, save_func):
			super().__init__(timeout=None)
			self.config = config
			self.save_func = save_func
			self.add_item(ConstantesGP.CategorySelect(config, save_func, self))

	class CategorySelect(discord.ui.Select):
		def __init__(self, config, save_func, parent_view):
			options = [discord.SelectOption(label=cat) for cat in config.keys() if cat != "GERAL"]
			super().__init__(placeholder="Escolha uma categoria...", options=options)
			self.config = config
			self.save_func = save_func
			self.parent_view = parent_view

		async def callback(self, interaction: discord.Interaction):
			categoria = self.values[0]
			await interaction.response.edit_message(content=f"Categoria **{categoria}** selecionada.", view=ConstantesGP.ItemView(self.config, self.save_func, self.parent_view, categoria))

	class ItemView(discord.ui.View):
		def __init__(self, config, save_func, parent_view, categoria):
			super().__init__(timeout=None)
			self.config = config
			self.save_func = save_func
			self.categoria = categoria
			self.parent_view = parent_view

			self.add_item(ConstantesGP.ItemSelect(config, save_func, self, categoria))
			self.add_item(discord.ui.Button(label="Voltar", style=discord.ButtonStyle.secondary, custom_id="voltar"))

		async def interaction_check(self, interaction: discord.Interaction) -> bool:
			if interaction.data["custom_id"] == "voltar":
				await interaction.response.edit_message(content="Selecione a categoria que deseja configurar:", view=self.parent_view)
				return False
			return True

	class ItemSelect(discord.ui.Select):
		def __init__(self, config, save_func, parent_view, categoria):
			options = [discord.SelectOption(label=key) for key in config[categoria].keys()]
			super().__init__(placeholder="Escolha um item para configurar...", options=options)
			self.config = config
			self.save_func = save_func
			self.parent_view = parent_view
			self.categoria = categoria

		async def callback(self, interaction: discord.Interaction):
			item = self.values[0]
			await interaction.response.send_modal(ConstantesGP.EditValueModal(self.config, self.save_func, self.categoria, item))

	with open("constantes.json", "r") as f:
		CONFIG = json.load(f)

	def save_config(self):
		with open("constantes.json", "w") as f:
			json.dump(self.CONFIG, f, indent=4)

	@app_commands.command(name="setup_view", description="Visualiza os dados de configuração.")
	async def setup_view(self, interaction: discord.Interaction):
		embed = discord.Embed(title="📑 Configurações atuais", color=discord.Color.blue())
		for categoria, valores in self.CONFIG.items():
			if categoria == "GERAL":
				safe_keys = {k: v for k, v in valores.items() if k not in ["SERVIDOR", "TOKEN"]}
				if safe_keys:
					embed.add_field(name=f"🔹 {categoria}", value="\n".join(f"**{k}**: `{v}`" for k, v in safe_keys.items()), inline=False)
			else:
				embed.add_field(name=f"🔹 {categoria}", value="\n".join(f"**{k}**: `{v}`" for k, v in valores.items()), inline=False)
		await interaction.response.send_message(embed=embed, ephemeral=True)

	@app_commands.command(name="setup_config", description="Configura os dados individualmente.")
	async def setup_config(self, interaction: discord.Interaction):
		await interaction.response.send_message("Selecione a categoria que deseja configurar:", view=self.SetupView(self.CONFIG, self.save_config), ephemeral=True)