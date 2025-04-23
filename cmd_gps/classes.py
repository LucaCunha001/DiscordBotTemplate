import aiohttp
import asyncio
import chat_exporter
import datetime
import discord
import io
import json
import os
import platform
from bs4 import BeautifulSoup

CONST_PATH = "constantes.json"

async def validar_token(token: str) -> bool:
	"""
	Valida se o token fornecido é um token de bot do Discord válido.

	Args:
		token (str): Token do bot.

	Returns:
		bool: True se o token for válido, False caso contrário.
	"""
	url = "https://discord.com/api/v10/users/@me"
	headers = {
		"Authorization": f"Bot {token}"
	}

	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers=headers) as resp:
			return resp.status == 200

async def validar_guild_id(guild_id: int, token: str) -> bool:
	"""
	Valida se o bot com o token informado está presente no servidor com o ID fornecido.

	Args:
		guild_id (int): ID do servidor (guild) do Discord.
		token (str): Token do bot.

	Returns:
		bool: True se o bot estiver no servidor, False caso contrário.
	"""
	url = f"https://discord.com/api/v10/guilds/{guild_id}"
	headers = {
		"Authorization": f"Bot {token}"
	}

	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers=headers) as resp:
			return resp.status == 200

async def setup_config():
	"""
	Executa a configuração inicial do bot, solicitando informações do usuário via terminal
	para criar o arquivo `constantes.json` com as configurações básicas.

	- Valida token e servidor.
	- Cria `requirements.txt` se não existir.
	- Verifica dependências adicionais (`cpu.py`).
	- Exibe mensagens de status no terminal.
	"""
	if not os.path.exists(CONST_PATH):
		while True:
			token = input("Insira o token do seu bot: ").strip()
			if await validar_token(token):
				break
			os.system("cls" if platform.system() == "Windows" else "clear")
			print("Token inválido, tente novamente.")
		os.system("cls" if platform.system() == "Windows" else "clear")
		while True:
			servidor = input("Insira o ID do seu servidor: ").strip()
			if not servidor.isdigit():
				print("Insira apenas números.")
				continue

			if await validar_guild_id(int(servidor), token):
				break
			os.system("cls" if platform.system() == "Windows" else "clear")
			print("ID de servidor inválido ou o bot não está nesse servidor.")
		os.system("cls" if platform.system() == "Windows" else "clear")
		constantes_ = {
			"GERAL": {
				"SERVIDOR": int(servidor),
				"STATUS": input("Insira os status padrão do Bot: "),
				"FORMULARIO": "",
				"TOKEN": token
			},
			"CATEGORIAS": {
				"CATEGORIA_CALLS": 0,
				"CATEGORIA_TICKETS": 0,
				"CATEGORIA_PARCERIAS": 0
			},
			"CANAIS": {
				"CANAL_GERAL": 0,
				"CANAL_TICKETS": 0,
				"CANAL_AVALIACAO": 0,
				"CANAL_CONVITES": 0,
				"CANAL_DIVULGACAO": 0,
				"CANAL_REGRAS": 0,
				"CANAL_ABRIR_TICKET": 0,
				"CANAL_FORMS": 0,
				"CANAL_STAFF_UPDATES": 0
			},
			"CARGOS": {
				"CARGOS_TICKETS": [0],
				"CARGO_PARCEIRO": 0,
				"CARGOS_DE_PROMOCAO": [0],
				"CARGO_DONOS": 0,
				"CARGO_DONOS_NOME": "Dono",
				"CARGO_BOT1": 0,
				"CARGO_BOT2": 0,
				"CARGO_MEMBRO": 0,
				"CARGO_MADMEWMEW": 0,
				"CARGO_JAFUIBOOSTER": 0,
				"CARGO_STAFF": 0,
				"CARGO_EXSTAFF": 0
			},
			"LOGS": {
				"LOG_GERAL": 0,
				"LOG_MSG_DEL": 0,
				"LOG_MSG_EDIT": 0,
				"LOG_CASTIGOS": 0
			}
		}

		with open('constantes.json', 'w', encoding='utf-8') as f:
			json.dump(constantes_, f)

		with open(CONST_PATH, "w") as f:
			json.dump(constantes_, f, indent=4)

		del constantes_

		print(f"Arquivo {CONST_PATH} criado com sucesso!")

	if not os.path.isfile('requirements.txt'):
		with open('requirements.txt', 'w', encoding='utf-8') as f:
			f.write('discord.py\npsutil\npillow\nchat_exporter\nbeautifulsoup4\nrequestsaiohttp\n')
	
	dependencias_ausentes = []

	for i in ['cpu']:
		if not os.path.isfile(f"{i}.py"):
			dependencias_ausentes.append(i)
	
	if dependencias_ausentes:
		class DepError(Exception):
			"""Exceção personalizada para dependências ausentes."""
			def __init__(self, error):
				super().__init__(error)
		
		raise DepError(f"Arquivos em falta: {', '.join(dependencias_ausentes)}")

	print("\nSetup finalizado!")

if __name__ == "__main__":
	asyncio.run(setup_config())

class ConstGroup:
	"""
	Representa um grupo de constantes lidas do arquivo JSON, armazenadas como atributos dinâmicos.
	"""
	def __init__(self, **kargs):
		for k, v in kargs.items():
			setattr(self, k, v)

	def __str__(self):
		"""Retorna a representação em string do dicionário de constantes."""
		return str(self.__dict__)

class Constantes:
	"""
	Classe principal para carregar e acessar as constantes do JSON.
	
	Os atributos são instâncias de `ConstGroup` quando os valores são dicionários.
	"""
	def __init__(self, json_data):
		for k, v in json_data.items():
			if isinstance(v, dict):
				setattr(self, k, ConstGroup(**v))
			else:
				setattr(self, k, v)

	def __getattr__(self, name):
		"""
		Permite acessar as constantes por atributo. Caso o atributo não exista, tenta buscar no dicionário `values`.
		"""
		return self.values.get(name)

	def __str__(self):
		"""Retorna a representação em JSON das constantes."""
		return json.dumps(self.values, indent=4)

# Carrega as constantes do arquivo constantes.json
with open("constantes.json", "r") as file:
	dados_json = json.load(file)

constantes = Constantes(dados_json)

class CallControlerModal(discord.ui.Modal):
	"""Modal para configuração de um canal de voz.

	Permite definir a quantidade máxima de usuários no canal.
	"""

	def __init__(self, canal: discord.VoiceChannel):
		"""
		Inicializa o modal de configuração de canal de voz.

		@param canal: O canal de voz a ser configurado.
		@type canal: discord.VoiceChannel
		"""
		super().__init__(title="Call Config", timeout=None, custom_id="CallConfigModal")
		self.canal = canal
		self.pergunta_quantidade_membros = discord.ui.TextInput(
			label="Quantidade máxima de membros",
			placeholder=self.canal.user_limit if self.canal.user_limit else "0",
			default=self.canal.user_limit if self.canal.user_limit else "0",
			custom_id="max_count",
			required=False,
			style=discord.TextStyle.short
		)
		self.add_item(self.pergunta_quantidade_membros)

	async def on_submit(self, interaction: discord.Interaction):
		"""Executado quando o usuário submete o modal."""
		await self.canal.edit(user_limit=int(self.pergunta_quantidade_membros.value) if self.pergunta_quantidade_membros.value else None)
		await interaction.response.send_message("Configurações alteradas com sucesso!", ephemeral=True)

class CallControlerButton(discord.ui.Button):
	"""Botão que abre o modal de configuração da call."""

	def __init__(self):
		"""Inicializa o botão de configuração."""
		super().__init__(style=discord.ButtonStyle.gray, label="Config", custom_id="CallConfigButton", emoji="⚙️")

	async def callback(self, interaction: discord.Interaction):
		"""Callback executada ao clicar no botão."""
		if interaction.message.embeds[0].description[len("Dono: <@"):-1] != str(interaction.user.id):
			return await interaction.response.send_message("Você precisa ser o dono do canal para fazer isso.", ephemeral=True)
		await interaction.response.send_modal(CallControlerModal(canal=interaction.channel))

class CallControllerView(discord.ui.View):
	"""View que contém o botão de configuração da call."""

	def __init__(self):
		"""Inicializa a view e adiciona o botão."""
		super().__init__(timeout=None)
		self.add_item(CallControlerButton())

class CallCreator(discord.ui.Select):
	"""Select menu para criar canais de voz categorizados."""

	def __init__(self, bot: discord.Client):
		"""Inicializa o select menu com opções de categorias de calls."""
		self.nomes = ["🏳️", "pacifista", "🌻", "neutra", "💀", "genocida", "🛠️", "mods", "⚡", "speedruns", "🏠", "fangames", "❓", "outros"]
		options = []
		for i in range(int(len(self.nomes) / 2)):
			i *= 2
			options.append(
				discord.SelectOption(label=self.nomes[i + 1].capitalize(), emoji=self.nomes[i], value=self.nomes[i + 1].lower())
			)
		super().__init__(
			placeholder="Crie um tipo de call",
			max_values=1,
			min_values=1,
			options=options,
			custom_id="call_creator"
		)
		self.bot = bot

	async def callback(self, interaction: discord.Interaction):
		"""Callback executada ao selecionar uma categoria."""
		value = int(self.nomes.index(self.values[0]))
		nome_ = self.nomes[value].capitalize()
		emoji = self.nomes[value - 1]
		categoria = self.bot.get_channel(constantes.CATEGORIAS.CATEGORIA_CALLS)
		nome = f"{emoji}・{nome_} {sum(1 for ch in categoria.voice_channels if ch.name.startswith(f'{emoji}・{nome_}')) + 1}"
		canal = await interaction.guild.create_voice_channel(name=nome, category=categoria)
		await canal.send(embed=discord.Embed(title="Configurações da call", description=f"Dono: {interaction.user.mention}", colour=interaction.user.color), view=CallControllerView())
		await interaction.response.send_message(f"Canal criado! {canal.mention}", ephemeral=True)

class CallCreatorView(discord.ui.View):
	"""View que contém o select menu para criação de calls."""

	def __init__(self):
		"""Inicializa a view e adiciona o select."""
		super().__init__(timeout=None)
		self.add_item(CallCreator())

class ModalPresence(discord.ui.Modal):
	"""Modal para definir a presença (status) do bot."""

	def __init__(self, tipo: str, bot: discord.Client):
		"""
		Inicializa o modal de presença.

		@param tipo: O tipo de presença (game, watch, listen, stream)
		@type tipo: str
		"""
		super().__init__(title="Adicionar plataforma")
		self.tipo = tipo
		self.texto = discord.ui.TextInput(label="Texto dos status", custom_id="txt")
		self.add_item(self.texto)
		if self.tipo == "stream":
			self.link = discord.ui.TextInput(label="Link da live", custom_id="linkar")
			self.add_item(self.link)
		self.bot = bot

	async def on_submit(self, modal_interaction: discord.Interaction):
		"""Callback executada ao submeter o modal."""
		if self.tipo == "game":
			await self.bot.change_presence(activity=discord.Game(name=self.texto.value))
		if self.tipo == "watch":
			await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=self.texto.value))
		if self.tipo == "listen":
			await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=self.texto.value))
		if self.tipo == "stream":
			if self.link.value.startswith("https://"):
				await self.bot.change_presence(activity=discord.Streaming(name=self.texto.value, url=self.link.value))
			else:
				await self.bot.change_presence(activity=discord.Streaming(name=self.texto.value, url="https://" + self.link.value))
		await modal_interaction.response.send_message("Status alterado com sucesso!", ephemeral=True)

class DropdownMenu(discord.ui.Select):
	"""Definir o tipo de status do Bot (Jogando, Assistindo, Ouvindo ou Transmitindo)."""
	def __init__(self):
		options = [
			discord.SelectOption(label="Jogando", value="game", emoji="🎮"),
			discord.SelectOption(label="Assistindo", value="watch", emoji="📺"),
			discord.SelectOption(label="Ouvindo", value="listen", emoji="🎧"),
			discord.SelectOption(label="Transmitindo", value="stream", emoji="📡")
		]
		super().__init__(
			placeholder = "Selecione qual o tipo de precense você quer.",
			max_values = 1,
			min_values = 1,
			options = options
		)
	async def callback(self, interaction: discord.Interaction):
		"""Muda a presença do Bot."""
		await interaction.response.send_modal(ModalPresence(tipo=self.values[0]))

class Dropdown(discord.ui.Select):
	"""Dropdown da abertura de tickets."""
	def __init__(self, bot: discord.Client):
		options = [
			discord.SelectOption(value="Comandos", label="Comandos", emoji="💻"),
			discord.SelectOption(value="suporte", label="Suporte Geral", emoji="📞"),
			discord.SelectOption(value="denunciar", label="Denunciar", emoji="🚨"),
			discord.SelectOption(value="parceria", label="Parceria", emoji="🤝")
		]
		super().__init__(
			placeholder="Como posso te ajudar?",
			min_values=1,
			max_values=1,
			options=options,
			custom_id="setup_de_ajuda"
		)
		self.bot = bot

	async def callback(self, interaction: discord.Interaction):
		"""Cada ação de acordo com a escolha do menu."""
		if self.values[0] == "Comandos":
			"""Mostra os comandos do Bot."""
			commands = await self.bot.http.get_global_commands(self.bot.user.id)
			comandos = {}
			for comando in commands:
				if 'options' in comando:
					for subcomando in comando['options']:
						if subcomando['type'] == 1:
							comandos[f"</{comando['name']} {subcomando['name']}:{comando['id']}>"]=subcomando.get('description', 'Sem descrição')
						else:
							comandos[f"</{comando['name']}:{comando['id']}>"] = comando.get('description', 'Sem descrição')
				else:
					comandos[f"</{comando['name']}:{comando['id']}>"] = comando.get('description', 'Sem descrição')
			embeds = []
			embed = discord.Embed(
				title="Comandos",
				description="Essa é a lista completa dos meus comandos:",
				colour=discord.Color.from_str("#ff0000")
			)
			for i, (comando, descricao) in enumerate(comandos.items(), 1):
				embed.add_field(name=comando, value=descricao)
				if i % 25 == 0:
					embeds.append(embed)
					embed = discord.Embed(
						title="Comandos (continuação)",
						description="Aqui estão mais comandos:",
						colour=discord.Color.from_str("#ff0000")
					)
			if embed.fields:
				embeds.append(embed)
			await interaction.response.send_message(embeds=embeds, ephemeral=True)
			return

		if self.values[0] == "suporte":
			"""Abre um ticket de suporte geral."""
			canal_existente = discord.utils.get(interaction.guild.text_channels, name="supor " + str(interaction.user.id))
			
			if not canal_existente:
				ids_cargos_permitidos = constantes.CARGOS.CARGOS_TICKETS
				
				overwrites = {
					interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
					interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
				}
				
				for cargo_id in ids_cargos_permitidos:
					cargo = interaction.guild.get_role(cargo_id)
					if cargo:
						overwrites[cargo] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

				canal_denun = await interaction.guild.create_text_channel(
					name="supor " + str(interaction.user.id),
					category=interaction.guild.get_channel(constantes.CATEGORIAS.CATEGORIA_TICKETS),
					overwrites=overwrites
				)
				supor_embed = discord.Embed(
					title="Suporte Geral",
					colour=discord.Color.green(),
					description=(
						"Olá! Estamos aqui para ajudar com qualquer dúvida que você tenha.\n\n"
						"Por favor, explique sua dúvida ou problema de forma clara e detalhada para que possamos auxiliá-lo da melhor maneira possível. "
						"Se possível, inclua informações como:\n"
						"- Qual é a sua dúvida ou dificuldade;\n"
						"- O que você já tentou para resolver;\n"
						"- Quais mensagens de erro ou comportamentos inesperados você observou;\n"
						"- Outros detalhes relevantes que possam ajudar na resolução.\n\n"
						"Nossa equipe fará o possível para responder rapidamente e solucionar sua questão!"
					)
				)
				supor_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
				await canal_denun.send(embed=supor_embed,
				view=TicketView(), content=f"{interaction.user.mention} <@&{constantes.CARGOS.CARGO_STAFF}>")
				embed = discord.Embed(
					title="Ticket criado!",
					colour=discord.Color.from_str("#ff0000")
				)
				view = discord.ui.View()
				link = discord.ui.Button(label="Ver ticket", url=f"https://discord.com/channels/{constantes.CATEGORIAS.CATEGORIA_TICKETS}/{canal_denun.id}", style=discord.ButtonStyle.link)
				view.add_item(link)
				await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
			else:
				embed.description = f"Você já possui um canal de ticket ativo: <#{canal_existente.id}>"
				await interaction.response.send_message(embed=embed, ephemeral=True)
		elif self.values[0] == "denunciar":
			"""Abre um ticket de denúncia."""
			canal_existente = discord.utils.get(interaction.guild.text_channels, name="denun " + str(interaction.user.id))
			
			if not canal_existente:
				ids_cargos_permitidos = constantes.CARGOS.CARGOS_TICKETS
				
				overwrites = {
					interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
					interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
				}
				
				for cargo_id in ids_cargos_permitidos:
					cargo = interaction.guild.get_role(cargo_id)
					if cargo:
						overwrites[cargo] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

				canal_denun = await interaction.guild.create_text_channel(
					name="denun " + str(interaction.user.id),
					category=interaction.guild.get_channel(constantes.CATEGORIAS.CATEGORIA_TICKETS),
					overwrites=overwrites
				)
				denun_embed = discord.Embed(
					title="Denúncia",
					colour=discord.Color.red(),
					description=(
						f"Olá, {interaction.user.display_name}.\n\n"
						"Recebemos sua solicitação para registrar uma denúncia. Por favor, descreva com o máximo de detalhes possível o ocorrido. "
						"Inclua informações relevantes, como:\n"
						"- O que aconteceu;\n"
						"- Quem está envolvido (se aplicável);\n"
						"- Quando e onde ocorreu o evento;\n"
						"- Outras informações que possam ajudar na análise.\n\n"
						"Garantimos que sua denúncia será tratada com seriedade e tomaremos as medidas necessárias."
					)
				)
				denun_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
				await canal_denun.send(embed=denun_embed,
				view=TicketView(), content=f"{interaction.user.mention} <@&{constantes.CARGOS.CARGO_STAFF}>")
				embed = discord.Embed(
					title="Ticket criado!",
					colour=discord.Color.from_str("#fe0000")
				)
				view = discord.ui.View()
				link = discord.ui.Button(label="Ver ticket", url=f"https://discord.com/channels/{constantes.CATEOGORIAS.CATEGORIA_TICKETS}/{canal_denun.id}", style=discord.ButtonStyle.link)
				view.add_item(link)
				await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
			else:
				embed.description = f"Você já possui um canal de ticket ativo: <#{canal_existente.id}>"
				await interaction.response.send_message(embed=embed, ephemeral=True)
		elif self.values[0] == "parceria":
			"""Abre um ticket de parceira."""
			canal_existente = discord.utils.get(interaction.guild.text_channels, name="parce " + str(interaction.user.id))
			
			if not canal_existente:
				ids_cargos_permitidos = constantes.CARGOS.CARGOS_TICKETS
				
				overwrites = {
					interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
					interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
				}
				
				for cargo_id in ids_cargos_permitidos:
					cargo = interaction.guild.get_role(cargo_id)
					if cargo:
						overwrites[cargo] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

				canal_parce = await interaction.guild.create_text_channel(
					name="parce " + str(interaction.user.id),
					category=interaction.guild.get_channel(constantes.CATEGORIAS.CATEGORIA_TICKETS),
					overwrites=overwrites
				)
				parce_embed = discord.Embed(
					title="Parceria",
					colour=discord.Color.red(),
					description="**Nosso ticket de parceria foi criado para facilitar a divulgação e o apoio mútuo entre servidores do Discord ou fangames relacionadas ao universo de Undertale!**\n\nAqui, você pode compartilhar seu projeto ou servidor com uma comunidade apaixonada por Undertale e suas fangames. Queremos ajudar a fortalecer laços entre criadores e fãs, promovendo servidores, projetos e ideias que compartilhem do mesmo espírito colaborativo e criativo.\n\n**Benefícios da parceria:**\n- Alcance mais público para o seu servidor ou fangame.\n- Troca de visibilidade entre comunidades com interesses em comum.\n- Criação de uma rede de apoio para projetos inspirados em Undertale."
				)
				parce_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
				await canal_parce.send(embed=parce_embed,
				view=TicketView(), content=f"{interaction.user.mention} <@&{constantes.CARGOS.CARGO_STAFF}>")
				embed = discord.Embed(
					title="Ticket criado!",
					colour=discord.Color.from_str("#ff0000")
				)
				view = discord.ui.View()
				link = discord.ui.Button(label="Ver ticket", url=f"https://discord.com/channels/{constantes.CATEGORIAS.CATEGORIA_TICKETS}/{canal_parce.id}", style=discord.ButtonStyle.link)
				view.add_item(link)
				await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
			else:
				embed.description = f"Você já possui um canal de ticket ativo: <#{canal_existente.id}>"
				await interaction.response.send_message(embed=embed, ephemeral=True)
		else:
			await interaction.response.send_message(embed=embed, ephemeral=True)

class TicketView(discord.ui.View):
	"""
	View do menu de tickets.
	"""
	def __init__(self, bot: discord.Client):
		super().__init__(timeout=None)
		self.bot = bot
		
	@discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.blurple, custom_id="fechar")
	async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
		"""
		Fecha o ticket e envia as mensagens nas logs.
		"""
		qm_abriu = interaction.message.mentions[-1]
		qm_fechou = interaction.user
		embed = discord.Embed(
			title="Ticket Finalizado",
			colour=discord.Color.from_str("#ff0000"),
			description=(
				"Um ticket foi finalizado e registrado no sistema."
			)
		)
		tipos={"sil": "Silencioso", "sup": "Suporte Geral", "den": "Denúcia", "bug": "Bug", "par": "Parceria", "tre": "Treinamento"}
		embed.add_field(name="Tipo", value=tipos[interaction.channel.name[:3]])
		embed.add_field(name="Aberto por", value=qm_abriu.mention)
		embed.add_field(name="Fechado por", value=qm_fechou.mention)
		embed.add_field(name="ID do ticket", value=interaction.channel.id)
		embed.set_thumbnail(url=interaction.guild.icon.url)
		embed.set_footer(text="Sistema de Gerenciamento de Tickets")
		embed.timestamp = datetime.datetime.now()
		await interaction.response.send_message(embed=embed)
		limite = 200
		mensagens = len([msg async for msg in interaction.channel.history()])
		transcript = await chat_exporter.export(interaction.channel, limit=limite, tz_info="America/Sao_Paulo", military_time=True, bot=self.bot)
		await interaction.channel.delete()
		soup = BeautifulSoup(transcript, "html.parser")
		for title in soup.find_all("title"):
			title.string = f"Transcript do Ticket: {interaction.channel.name} - {interaction.channel.id}"
		for tipo in ["title", "og:title", "twitter:title"]:
			for title in soup.find_all("meta", property=tipo):
				title.content = f"Transcript do Ticket: {interaction.channel.name} - {interaction.channel.id}"
			for title in soup.find_all("meta", {"name": tipo}):
				if title.has_attr('content'):
					title['content'] = f"Transcript do Ticket: {interaction.channel.name} - {interaction.channel.id}"
				title.content = f"Transcript do Ticket: {interaction.channel.name} - {interaction.channel.id}"
		for meta in soup.find_all("div", class_="meta__title"):
			casos = {"Guild ID": "ID do Servidor", "Channel ID": "ID do Canal", "Channel Creation Date": "Data de Criação do Canal", "Total Message Count": "Quantidade Total de Mensagens", "Total Message Participants": "Total de Participantes nas Mensagens", "Member Since": "Membro Desde", "Member ID": "ID do Membro", "Message Count": "Quantidade de Mensagens"}
			meta.string = casos.get(meta.string, meta.string)
		data_hoje = datetime.datetime.now()
		meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
		mes = meses[data_hoje.month - 1]
		data_formatada = f"{data_hoje.day} de {mes.title()} de {data_hoje.year} às {data_hoje.hour:02d}:{data_hoje.minute:02d}:{data_hoje.second:02d}"
		for tipo in ["description", "og:description", "twitter:description"]:
			for description in soup.find_all("meta", {"name": tipo}):
				description["content"] = f"Transcript do Ticket: {interaction.channel.name} - {interaction.channel.id}. Com {mensagens} mensagens. O transcript foo gerado em {data_formatada}"
			for description in soup.find_all("meta", property=tipo):
				if description.has_attr('content'):
					description["content"] = f"Transcript do Ticket: {interaction.channel.name} - {interaction.channel.id}. Com {mensagens} mensagens. O transcript foi gerado em {data_formatada}"
		for span in soup.find_all("span"):
			if span.string =="Summary": 
				span.string="Sumário"
		for span in soup.find_all("span", class_="info__title"):
			span.string = f"Bem-vindo ao canal #{interaction.channel.name}!"
		for span in soup.find_all("span", class_="footer__text"):
			span.string = f"Esse transcript foi gerado em {data_formatada}"
		for span in soup.find_all("span", class_="info__subject"):
			span.string = f"Essas são aos últimas {limite} mensagens do canal #{interaction.channel.name}."
		for script in soup.find_all("span"):
			if script.string:
				script.string = script.string.replace("Today at", "Hoje às")
				script.string = script.string.replace("Yesterday at", "Ontem às")
				script.string = script.string.replace("Tomorrow at", "Amanhã às")
		modfied_transcript = str(soup)
		transcript_file = discord.File(
			io.BytesIO(modfied_transcript.encode()),
			filename=f"ticket-{interaction.channel.id}.html")
		transcript_file2 = discord.File(
			io.BytesIO(modfied_transcript.encode()),
			filename=f"ticket-{interaction.channel.id}.html")
		try:
			await qm_abriu.send(embed=embed, file=transcript_file)
		except discord.Forbidden:
			print("Não consegui enviar a DM ao usuário, permissão negada.")
		except Exception as e:
			print(f"Erro ao enviar a DM: {e}")
		tickets = self.bot.get_channel(constantes.CANAIS.CANAL_TICKETS)
		await tickets.send(embed=embed, file=transcript_file2)
	
	@discord.ui.button(label="Adicionar Membro", style=discord.ButtonStyle.green, custom_id="add_member")
	async def add_member(self, interaction: discord.Interaction, button: discord.ui.Button):
		"""
		Adiciona um membro ao ticket.
		"""
		modal = AddMemberModal(interaction.channel)
		await interaction.response.send_modal(modal)

	@discord.ui.button(label="Remover Membro", style=discord.ButtonStyle.red, custom_id="remove_member")
	async def remove_member(self, interaction: discord.Interaction, button: discord.ui.Button):
		"""
		Remove um membro do ticket.
		"""
		modal = RemoveMemberModal(interaction.channel)
		await interaction.response.send_modal(modal)
	
	@discord.ui.button(label="Pingar", custom_id="ping", style=discord.ButtonStyle.gray)
	async def ping_member(self, interaction: discord.Interaction, button: discord.ui.Button):
		"""
		Pinga o membro ou o staff responsável pelo ticket.
		"""
		historico: list[discord.Message] = [msg async for msg in interaction.channel.history()]
		author = None
		for msg in historico:
			if msg.author.bot:
				continue
			if author != msg.author and author:
				return await interaction.response.send_message(msg.author.mention, embed=discord.Embed(title="Ei, você está aí?", description="Precisamos continuar o ticket!"))
			author = msg.author
		await interaction.response.send_message(author.mention, ephemeral=True)

class AddMemberModal(discord.ui.Modal):
	"""
	Adiciona um membro ao ticket.
	"""
	def __init__(self, channel: discord.TextChannel):
		super().__init__(title="Adicionar Membro")
		self.channel = channel

		self.add_item(discord.ui.TextInput(
			label="ID do Usuário",
			placeholder="Digite o ID do usuário que deseja adicionar",
			style=discord.TextStyle.short
		))

	async def on_submit(self, interaction: discord.Interaction):
		"""
		Adiciona o membro indicado ao ticket.
		"""
		await interaction.response.defer(ephemeral=True)
		user_id = self.children[0].value.strip()
		guild = interaction.guild
		try:
			member = guild.get_member(int(user_id))
			if member:
				await self.channel.set_permissions(member, read_messages=True, send_messages=True)
				await interaction.followup.send(f"O membro {member.mention} foi adicionado ao ticket.")
			else:
				await interaction.followup.send("Usuário não encontrado no servidor.", ephemeral=True)
		except Exception as e:
			await interaction.followup.send(f"Erro ao adicionar membro: {e}", ephemeral=True)

class RemoveMemberModal(discord.ui.Modal):
	"""
	Remove um membro do ticket.
	"""
	def __init__(self, channel: discord.TextChannel):
		super().__init__(title="Remover Membro")
		self.channel = channel

		self.add_item(discord.ui.TextInput(
			label="ID do Usuário",
			placeholder="Digite o ID do usuário que deseja remover",
			style=discord.TextStyle.short
		))

	async def on_submit(self, interaction: discord.Interaction):
		"""
		Remove o membro indicado do ticket.
		"""
		await interaction.response.defer(ephemeral=True)
		user_id = self.children[0].value.strip()
		guild = interaction.guild
		try:
			member = guild.get_member(int(user_id))
			if member:
				await self.channel.set_permissions(member, overwrite=None)
				await interaction.followup.send(f"O membro {member.mention} foi removido do ticket.")
			else:
				await interaction.followup.send("Usuário não encontrado no servidor.", ephemeral=True)
		except Exception as e:
			await interaction.followup.send(f"Erro ao remover membro: {e}", ephemeral=True)

class DropdownView(discord.ui.View):
	"""
	View do Dropdown de tickets.
	"""
	def __init__(self, dropdown=Dropdown()):
		super().__init__(timeout=None)
		self.add_item(dropdown)