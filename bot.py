import asyncio
import datetime
import json
import re
import discord
from cmd_gps.classes import constantes, DropdownView, TicketView, CallCreatorView, CallControllerView, DropdownMenu
from cpu import InfoCommands
from discord import app_commands
from embed_model import EmbedModelCommands

class Parceria(app_commands.Group):
	"""
	Comandos de parceria.
	"""
	def __init__(self, bot: discord.Client):
		super().__init__(name="parceria", description="Veja os tipos de parceria")
		self.bot=bot
	
	@app_commands.command(name="paga", description="Parceria paga")
	async def paga(self, interaction: discord.Interaction):
		"""
		Mensagem de parceria paga.
		"""
		await interaction.response.send_message("No momento, apenas a parceria gratuita", ephemeral=True)
	
	@app_commands.command(name="gratuita", description="Parceria gratuita")
	async def gratuita(self, interaction: discord.Interaction):
		"""
		Mensagem de parceria gratuita.
		"""
		membros = sum(1 if not membro.bot else 0 for membro in interaction.guild.members) +1
		embed = discord.Embed(title="Requisitos para parceria gratuita (Apenas servidores de Discord)", description=f"1 - Estar de acordo com as <#1288597922266480732>\n\n2 - Siga os **[termos do Discord](https://discord.com/terms)**\n\n3 - Ter no mínimo metade da quantidade de membros que o True Reset tem: `{int(membros/2)}`\n\n4 - Tenha um **texto** para sua parceria.\n\n-# Se cumprir aos requisitos, converse com o dono, {interaction.guild.owner.mention}", timestamp=None, colour=discord.Color.from_str("#ff0000"))
		embed.set_author(name=interaction.guild.owner.name, icon_url=interaction.guild.owner.avatar.url if interaction.guild.owner.avatar else interaction.guild.owner.default_avatar.url)
		embed.set_thumbnail(url=interaction.guild.icon.url)
		await interaction.response.send_message(embed=embed)
	
	@app_commands.command(name="setup", description="Faça uma parceria")
	async def setup_parceria(self, interaction: discord.Interaction, parceiro: discord.Member, emoji: str, canal: str):
		"""
		Configurar canal de parceria.
		"""
		if interaction.user.id != interaction.guild.owner.id:
			return await interaction.response.send_message("Acha que é fácil assim, rapaz? Quem você pensa que é? Cris Bumstead? O Cbum? Eu acho que não.", ephemeral=True)
		overwrites = {
			interaction.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
			parceiro: discord.PermissionOverwrite(read_messages=True, send_messages=True)
		}
		canal_parce = await interaction.guild.create_text_channel(
			name=f"{emoji}・{canal}",
			category=interaction.guild.get_channel(constantes.CATEGORIAS.CATEGORIA_PARCERIAS),
			overwrites=overwrites
		)
		await parceiro.add_roles(interaction.guild.get_role(constantes.CARGOS.CARGO_PARCEIRO))
		await interaction.response.send_message(f"Canal criado: {canal_parce.mention}")

class client(discord.Client):
	"""
	Classe do Bot.
	"""
	def __init__(self):
		super().__init__(intents=discord.Intents.all())
		self.synced = False
	
	async def setup_hook(self) -> None:
		"""
		Views eternas.
		"""
		self.add_view(DropdownView())
		self.add_view(TicketView(bot=self))
		self.add_view(CallCreatorView())
		self.add_view(CallControllerView())
	
	async def on_ready(self):
		"""
		Setup do Bot.
		"""
		servidor = bot.get_guild(constantes.GERAL.SERVIDOR)
		await self.wait_until_ready()
		cargos_de_promocao = constantes.CARGOS.CARGOS_DE_PROMOCAO
		cargos_de_promocao1 = [servidor.get_role(i) for i in cargos_de_promocao if servidor.get_role(i)]
		if not self.synced:
			tree.add_command(InfoCommands(self))
			tree.add_command(Parceria(self))
			tree.add_command(EmbedModelCommands(self))
			await self.carregar_comandos_externos(cargos_de_promocao=cargos_de_promocao, cargos_de_promocao1=cargos_de_promocao1)
			await tree.sync()
			self.synced = True
			print(f"Entramos como {self.user.name}!")
			print(f"Que tem o ID {self.user.id}")
			await bot.change_presence(activity=discord.Game(name=constantes.GERAL.STATUS))
	
	async def carregar_comandos_externos(self, cargos_de_promocao, cargos_de_promocao1):
		"""
		Carregar os comandos da pasta cmd_gps/.
		"""
		from cmd_gps.mod import Moderação
		from cmd_gps.staff import ComandosStaff
		tree.add_command(ComandosStaff(bot=self, lista_=[app_commands.Choice(name=cargo.name, value=str(cargo.id)) for cargo in cargos_de_promocao1], cargos_de_promocao=cargos_de_promocao))
		tree.add_command(Moderação(bot=self, constantes=constantes, enviar_log=enviar_log))

bot = client()
tree = app_commands.CommandTree(bot)

@tree.command(name="comandos", description="Veja quais comandos eu tenho")
async def ver_comands(interaction: discord.Interaction):
	await interaction.response.defer(ephemeral=True)
	commands = await bot.http.get_global_commands(bot.user.id)
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
	embed = discord.Embed(title="Comandos", description="Essa é a lista completa dos meus comandos:", colour=discord.Color.from_str("#ff0000"))
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
	await interaction.followup.send(embeds=embeds)

Regras = {
	"Regras de chat": [
		{
			"name": "Respeito Mútuo",
			"value": "Trate todos os membros com respeito. Não serão tolerados insultos, assédio, discriminação ou qualquer forma de comportamento tóxico."
		},
		{
			"name": "Conteúdo Apropriado",
			"value": "Mantenha o conteúdo das conversas apropriado. Isso inclui evitar linguagem ofensiva, conteúdo NSFW, e discussões sobre tópicos sensíveis que possam incomodar os outros."
		},
		{
			"name": "Sem Spam",
			"value": "Evite enviar mensagens repetidas, links não solicitados ou conteúdo irrelevante. Isso inclui mensagens em massa e promoções sem permissão."
		},
		{
			"name": "Drogas",
			"value": "É proibido fazer apologia ou qualquer referência a drogas, sejam lícitas ou ilícitas."
		},
		{
			"name": "Privacidade",
			"value": "Não compartilhe informações pessoais suas ou de outros membros. Respeite a privacidade de todos."
		},
		{
			"name": "Perfil inadequado",
			"value": "Perfis com conteúdos inadequados que violam as refras também serão punidos"
		},
		{
			"name": "Canal Adequado",
			"value": "Utilize os canais para seus propósitos específicos. Verifique as descrições dos canais e mantenha as discussões relevantes ao tema."
		},
		{
			"name": "Uso de Bots",
			"value": "Siga as diretrizes para interagir com bots. Não abuse de comandos ou provoque mal funcionamento."
		},
		{
			"name": "Decisões da Moderação",
			"value": "Os moderadores têm a palavra final em questões de moderação. Respeite suas decisões e orientações."
		},
		{
			"name": "Denúncias",
			"value": "Se você observar comportamento inadequado, informe a um moderador ou admin. Faça isso de forma privada."
		},
		{
			"name": "Colaboração",
			"value": "Sinta-se à vontade para contribuir com ideias e sugestões para melhorar o servidor. O feedback construtivo é sempre bem-vindo!"
		},
		{
			"name": "Diversão",
			"value": "Acima de tudo, divirta-se! Este é um espaço para todos desfrutarem de conversas e interações."
		}
	]
}

INVITE_REGEX = re.compile(r"(?:https?://)?discord(?:app\.com/invite|\.gg)/[a-zA-Z0-9]+")
URL_REGEX = re.compile(r"https?://[^\s/$.?#].[^\s]*")

bug = "||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|| _ _ _ _ _ _"

@tree.command(name="say", description="O que você acha")
async def say(interaction: discord.Interaction, texto: str, responder: str=None, digitar: bool=True):
	if interaction.user.id not in interaction.guild.get_role(constantes.CARGOS.CARGO_DONOS).members:
		await interaction.response.send_message("VOCÊ NÃO PODE FAZER ISSO, NYEH HEH HEH", ephemeral=True)
		return
	await interaction.response.send_message("Pronto", ephemeral=True)
	async with interaction.channel.typing():
		if digitar:
			await asyncio.sleep(len(texto)/10)
		texto = texto.replace("(bug)", bug)
		if responder:
			mensagem: discord.Message = await interaction.channel.fetch_message(int(responder))
			await mensagem.reply(texto)
			return
		await interaction.channel.send(texto)

async def boost(membro: discord.Member):
	geral = bot.get_channel(constantes.CANAIS.CANAL_GERAL)
	embed=discord.Embed(
		title="🎉 Novo Booster!",
		description=f"✨ {membro.mention} acabou de impulsionar o servidor!\nObrigado por ajudar a tornar nossa comunidade ainda mais incrível!\n\nCada boost é um passo para algo incrível! Obrigado por apoiar nosso servidor!",
		colour=discord.Color.from_str("#00ffff")
	)
	embed.set_thumbnail(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)
	embed.set_image(url="https://cdn.discordapp.com/attachments/955972869505024020/1325490299874836510/booster.gif?ex=677fef09&is=677e9d89&hm=64572197d034c5b9a2bbba86b9da8ad7293871c5087ca7c827c2c4bb0cbe2195&")
	embed.timestamp = datetime.datetime.now()
	await geral.send(embed=embed)

async def enviar_log(tipo: str, descrição: str, por: discord.Member, arquivo: discord.File = None, canal: int = constantes.LOGS.LOG_GERAL):
	canal: discord.TextChannel = bot.get_channel(canal)
	embed = discord.Embed(
		title=tipo,
		description=descrição
	)
	embed.set_author(url=f"https://discord.com/users/{por.id}", name=por.display_name, icon_url=por.guild_avatar.url if por.guild_avatar else por.avatar.url if por.avatar else por.default_avatar.url)
	await canal.send(embed=embed, file=arquivo)
	
@bot.event
async def on_voice_state_update(membro: discord.Member, antes: discord.VoiceState, depois: discord.VoiceState):
	if not depois.channel and antes.channel.category.id == constantes.CATEGORIAS.CATEGORIA_CALLS and len(antes.channel.members) == 0:
		await antes.channel.delete()

@bot.event
async def on_message(mensagem: discord.Message):
	if mensagem.author == bot.user:
		return
	match_ = INVITE_REGEX.search(mensagem.content)
	if match_:
		invite_url = match_.group()
		try:
			invite = await bot.fetch_invite(invite_url.split("/")[-1])
			
			if not invite.guild or not invite.guild.id == mensagem.guild.id:
				tobyfox = mensagem.guild.get_role(constantes.CARGOS.CARGO_DONOS)
				if tobyfox not in mensagem.author.roles:
					parceiro_cg = mensagem.guild.get_role(constantes.CARGOS.CARGO_PARCEIRO)
					if parceiro_cg not in mensagem.author.roles or mensagem.channel.category.id not in [constantes.CATEGORIAS.CATEGORIA_PARCERIAS, constantes.CATEGORIAS.CATEGORIA_TICKETS]:
						await mensagem.reply(f"{mensagem.author.mention}, você não pode compartilhar convites de outros servidores aqui!")
						log=bot.get_channel(constantes.CANAIS.CANAL_CONVITES)
						await log.send(embed=discord.Embed(title="Convite bloqueado.", description=f"{mensagem.author.mention} enviou o convite para o servidor {invite.guild.name} ({invite.guild.id}): `{invite_url}`").set_thumbnail(url=mensagem.author.avatar.url if mensagem.author.avatar else mensagem.author.default_avatar.url))
						await mensagem.delete()
						await mensagem.author.timeout(datetime.timedelta(minutes=60), reason="Enviando convites de servidores")
		except discord.Forbidden:
			print("Permissão insuficiente para buscar informações do convite.")
		except discord.HTTPException as e:
			print(f"Erro ao tentar verificar o convite: {e}")
		except Exception as e:
			print(e)
	match_=URL_REGEX.search(mensagem.content)
	if not match_ and mensagem.channel.id == constantes.CANAIS.CANAL_DIVULGACAO and not any(cg.id == constantes.CARGOS.CARGO_STAFF for cg in mensagem.author.roles):
		await mensagem.delete()
	emojis_proibidos = ["🍆", "🍒", "🍑", "🌸", "💦", "🔞", "👅", "🤤", "🍌", "💧", "👉", "👌", "🥵"]
	everyone_role = mensagem.guild.default_role
	canal_privado = not mensagem.channel.permissions_for(everyone_role).read_messages
	if not canal_privado and any(emoji in mensagem.content for emoji in emojis_proibidos) and not any(cg.id == constantes.CARGOS.CARGO_STAFF for cg in mensagem.author.roles):
		await mensagem.reply(f"{mensagem.author.mention}, esse emoji não é permitido.")
		await mensagem.author.timeout(datetime.timedelta(minutes=5), reason="Emojis sugestivos")
		await mensagem.delete()
	if mensagem.channel.id == constantes.CANAIS.CANAL_REGRAS:
		embeds = []
		for topico in Regras:
			embed = discord.Embed(
				title=topico,
				colour=discord.Color.from_str("#ff0000")
			)
			for regra_ in range(len(Regras[topico])):
				regra = Regras[topico][regra_]
				embed.add_field(name=f"{regra_+1} - {regra['name']}", value=regra["value"], inline=False)
			embeds.append(embed)
		async for msg in mensagem.channel.history():
			await msg.delete()
		await mensagem.channel.send(embeds=embeds)

	if mensagem.channel.id == constantes.CANAIS.CANAL_ABRIR_TICKET:
		async for mensagem in mensagem.channel.history():
			await mensagem.delete()
		embed = discord.Embed(title="Abertura de Ticket", colour=discord.Color.blue(), description="Olá! Bem-vindo ao sistema de tickets.\n\nCaso precise de ajuda, clique no botão abaixo para abrir um ticket. Nossa equipe estará pronta para auxiliá-lo assim que possível.\n\n**Lembre-se:**\n- Explique sua dúvida ou problema com o máximo de detalhes;\n- Aguarde pacientemente pela resposta da equipe;\n- Evite abrir múltiplos tickets para o mesmo problema.")
		embed.set_footer(text="Estamos aqui para ajudar!")
		embed.set_thumbnail(url=mensagem.guild.icon)
		await mensagem.channel.send(embed=embed, view=DropdownView())

@bot.event
async def on_member_join(membro: discord.Member):
	await membro.add_roles(*[membro.guild.get_role(constantes.CARGOS.CARGO_BOT1), membro.guild.get_role(constantes.CARGOS.CARGO_BOT2)]) if membro.bot else await membro.add_roles(membro.guild.get_role(constantes.CARGOS.CARGO_MEMBRO))
	if membro.id == 943289140265512991:
		await membro.add_role(membro.guild.get_role(constantes.CARGOS.CARGO_MADMEWMEW))
	await enviar_log(tipo="Bot adicionado" if membro.bot else "Novo membro!", descrição=f"O membro {membro.mention} entrou no servidor", por=membro)
	with open("exp.json", "r") as f:
		exp = json.load(f)
	exp[str(membro.id)] = {"exp": 0, "hp": 20}
	with open("exp.json", "w") as f:
		json.dump(exp, f, indent=4)
	embed = discord.Embed(
		title=f"🌟 Bem-vindo(a) ao servidor {membro.guild.name}! 🌟",
		description=f"Olá, {membro.mention}! É um prazer ter você conosco. Aqui estão algumas coisas importantes para você começar:",
		colour=discord.Color.from_str("#ff0000")
	)
	regras = [
		"Respeito acima de tudo!",
		"Trate todos os membros com gentileza e respeito. Queremos um ambiente seguro e divertido para todos!",
		"Explore os canais!",
		"Cada canal tem um propósito. Certifique-se de usá-los corretamente para manter a organização do servidor.",
		"Regras básicas:",
		"- Nada de spam ou flood.\n- Evite conteúdo impróprio ou fora das diretrizes.\n- Denúncias? Use o canal apropriado e conte com a nossa equipe.",
		"Dúvidas ou Ajuda?",
		"Nossa equipe de staff está aqui para ajudar. Não hesite em chamar um membro da staff se precisar de algo.",
		"Divirta-se e aproveite a estadia!",
		"Estamos ansiosos para ver você participando e contribuindo para tornar este servidor ainda mais incrível.\n\nVamos juntos explorar o universo de Undertale!"
	]
	for i in range(0, len(regras), 2):
		embed.add_field(name=regras[i], value=regras[i+1], inline=False)
	try:
		await membro.send(embed=embed)
	except discord.Forbidden:
		return

@bot.event
async def on_message_delete(msg: discord.Message):
	if not msg.author.bot:
		await enviar_log(canal=constantes.LOGS.LOG_MSG_DEL, tipo="Mensagem apagada", descrição=f"Uma mensagem de {msg.author.mention} foi apagada em {msg.channel.mention}:\n```{msg.content}```", por=msg.author)

@bot.event
async def on_message_edit(antes: discord.Message, depois: discord.Message):
	if not antes.author.bot:
		await enviar_log(canal=constantes.LOGS.LOG_MSG_EDIT, tipo="Mensagem editada", descrição=f"Uma mensagem de {antes.author.mention} foi editada em {antes.channel.mention}:\n**ANTES:** ```{antes.content}``` **DEPOIS:**```{depois.content}```", por=antes.author)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
	if after.premium_since is not None and before.premium_since != after.premium_since:
		await boost(after)
		await after.add_roles(after.guild.get_role(constantes.CARGOS.CARGO_JAFUIBOOSTER))
	#before_roles = {role.id for role in before.roles}
	#after_roles = {role.id for role in after.roles}

	if before.is_timed_out() != after.is_timed_out():
		guild = after.guild
		moderator = "Automod"
		motivo = None
		
		if guild.me.guild_permissions.view_audit_log:
			async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
				if entry.target.id == after.id:
					moderator = entry.user.mention
					motivo = entry.reason or "Não especificado"
					break
		if after.is_timed_out():
			timeout_end = f"<t:{int(after.timed_out_until.timestamp())}:R>" if after.timed_out_until else "Desconhecida"
			embed = discord.Embed(
				title="Membro em Castigo (Timeout)",
				description=f"{after.mention} foi colocado em timeout em {after.guild.name}.",
				colour=discord.Color.orange()
			)
			embed.add_field(name="ID do Membro:", value=after.id)
			embed.add_field(name="Colocado em timeout por:", value=moderator)
			embed.add_field(name="Duração do Timeout:", value = timeout_end)
			embed.add_field(name="Motivo:", value = motivo)
			embed.set_thumbnail(url=after.avatar.url if after.avatar else after.default_avatar.url)
		else:
			embed = discord.Embed(
				title="Castigo Removido (Timeout)",
				description=f"{after.mention} teve o timeout removido em {after.guild.name}.",
				colour=discord.Color.green()
			)
			embed.add_field(name="ID do Membro:", value=after.id)
			embed.add_field(name="Timeout removido por:", value=moderator)
			embed.set_thumbnail(url=after.avatar.url if after.avatar else after.default_avatar.url)
		
		canal2 = bot.get_channel(constantes.LOGS.LOG_CASTIGOS)

	elif before.display_name != after.display_name:
		canal2 = bot.get_channel(constantes.LOGS.LOG_APELIDOS)
		embed = discord.Embed(
			title="Apelido alterado",
			description=f"{after.mention} teve seu nome alterado de `{before.display_name}` para `{after.display_name}`"
		)
	
	else:
		return
	canal1 = bot.get_channel(constantes.LOGS.LOG_PUNICOES)
	await canal1.send(embed=embed)
	await canal2.send(embed=embed)

@bot.event
async def on_member_remove(member: discord.Member):
	try:
		await member.guild.fetch_ban(member)
		return
	except Exception as e:
		del e
		pass
	cargos_staff = [constantes.CARGOS.CARGO_STAFF]
	for cargo_id in cargos_staff:
		if discord.utils.get(member.roles, id=cargo_id):
			from cmd_gps.staff import pegar_imagem
			canal_log = bot.get_channel(constantes.CANAIS.CANAL_STAFF_UPDATES)
			embed = discord.Embed(
				title="🚨 Um membro da staff saiu!",
				description=(
					f"O membro {member.mention} saiu do servidor. "
					"Agradecemos pelo tempo que ele(a) contribuiu para a comunidade. 🙌"
				),
				color=discord.Color.red()
			)
			embed.set_footer(text=f"ID do usuário: {member.id}")
			embed.set_thumbnail(url=member.display_avatar.url)
			embed.set_image(url=pegar_imagem(member.guild.get_role(constantes.CARGOS.CARGO_MEMBRO), False))
			await canal_log.send(embed=embed)
			break
	embed = discord.Embed(
		title="Membro Expulso",
		description=f"{member.mention} foi expulso de {member.guild.name}.",
		colour=discord.Color.red()
	)

	moderator = None
	motivo = None
		
	if member.guild.me.guild_permissions.view_audit_log:
		async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
			if entry.target.id == member.id:
				moderator = entry.user.mention
				motivo = entry.reason  or "Não especificado"
				break
	if not moderator:
		return
			
	embed.add_field(name="ID do Membro:", value=member.id)
	embed.add_field(name="Expulso por:", value=moderator)
	if motivo:
		embed.add_field(name="Motivo", value=motivo)
	embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
	
	canal1 = bot.get_channel(constantes.LOGS.LOG_PUNICOES)
	canal2 = bot.get_channel(constantes.LOGS.LOG_KICKS)
	await canal1.send(embed=embed)
	await canal2.send(embed=embed)

@bot.event
async def on_member_ban(guild: discord.Guild, user: discord.User):
	embed = discord.Embed(
		title="Membro Banido",
		description=f"{user.mention} foi banido.",
		colour=discord.Color.from_str("#ff0000")
	)

	moderator = None
	motivo = None
		
	if guild.me.guild_permissions.view_audit_log:
		async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
			if entry.target.id == user.id:
				moderator = entry.user.mention
				motivo = entry.reason
				break

	embed.add_field(name="ID do Membro:", value=user.id)
	embed.add_field(name="Banido por:", value=moderator)
	if motivo:
		embed.add_field(name="Motivo", value=motivo)
	embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
	
	canal1 = bot.get_channel(constantes.LOGS.LOG_PUNICOES)
	canal2 = bot.get_channel(constantes.LOGS.LOG_BAN)
	await canal1.send(embed=embed)
	await canal2.send(embed=embed)

@bot.event
async def on_member_unban(guild: discord.Guild, user: discord.User):
	canal1 = guild.get_channel(constantes.LOGS.LOG_PUNICOES)
	canal2 = guild.get_channel(constantes.LOGS.LOG_UNBAN)
	moderator = "Desconhecido"
	motivo = None
	if guild.me.guild_permissions.view_audit_log:
		async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
			if entry.target.id == user.id:
				moderator = entry.user.mention
				motivo = entry.reason or "Não especificado"
				break

	embed = discord.Embed(
		title="Membro Desbanido",
		description=f"{user.mention} foi desbanido.",
		colour=discord.Color.from_str("#00ff00")
	)
	embed.add_field(name="ID do Membro", value=user.id, inline=True)
	embed.add_field(name="Desbanido Por", value=moderator, inline=False)
	embed.add_field(name="Motivo", value=motivo, inline=False)
	embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)

	await canal1.send(embed=embed)
	await canal2.send(embed=embed)

@tree.command(name="mudar_presenca", description="Mude a presença do Bot")
async def mudar_presenca(interaction: discord.Interaction):
	if interaction.user.id != interaction.guild.owner_id:
		return
	view = discord.ui.View()
	view.add_item(DropdownMenu())
	await interaction.response.send_message(content="Escolha o tipo de presença que você quer", view=view, ephemeral=True)

@tree.command(name="boost_message", description="Envia uma mensagem de boost")
@app_commands.checks.has_permissions(administrator=True)
async def boost_message(interaction: discord.Interaction):
	if interaction.user == interaction.guild.owner:
		await boost(interaction.user)
		await interaction.response.send_message("Mensagem de boost enviada com sucesso!", ephemeral=True)

@tree.command(name="membros")
async def membros(interaction: discord.Interaction):
	embed = discord.Embed(
		title="Membros",
		description="Informações sobre os membros do servidor",
		colour=discord.Color.random()
	)
	
	membros = interaction.guild.member_count
	bots = sum(1 for membro in interaction.guild.members if membro.bot)

	online = sum(1 for membro in interaction.guild.members if membro.status == discord.Status.online and not membro.bot)
	dnd = sum(1 for membro in interaction.guild.members if membro.status == discord.Status.dnd and not membro.bot)
	idle = sum(1 for membro in interaction.guild.members if membro.status == discord.Status.idle and not membro.bot)
	offline = sum(1 for membro in interaction.guild.members if membro.status == discord.Status.offline and not membro.bot)
	boosters = sum(1 for membro in interaction.guild.members if membro.premium_since is not None)
	ja_boosters = interaction.guild.get_role(constantes.CARGOS.CARGO_JAFUIBOOSTER)
	ja_boosters = len(ja_boosters.members)
	embed.add_field(name="Membros", value=f"`{membros-bots}`")
	embed.add_field(name="Bots", value=f"`{bots}`")
	embed.add_field(name="Usuários totais", value=f"`{membros}`")
	embed.add_field(name="Online", value=f"`{online}`")
	embed.add_field(name="DND", value=f"`{dnd}`")
	embed.add_field(name="Ausente", value=f"`{idle}`")
	embed.add_field(name="Offline", value=f"`{offline}`")
	embed.add_field(name="Boosters", value=f"`{boosters}`")
	embed.add_field(name="Já deram Boosts", value=f"`{ja_boosters}`")

	if interaction.guild.icon:
		embed.set_thumbnail(url=interaction.guild.icon.url)

	await interaction.response.send_message(embed=embed)

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
	texto = ""
	if isinstance(error, app_commands.CheckFailure):
		texto = "Você não tem permissão para usar este comando."
	else:
		texto =f"Ocorreu um erro: {error}"
	for i in [interaction.response.send_message, interaction.response.edit_message, interaction.followup.edit_message, interaction.followup.send]:
		try:
			await i(content=texto, ephemeral=True)
			return
		except Exception as e:
			del e

bot.run(constantes.GERAL.TOKEN)