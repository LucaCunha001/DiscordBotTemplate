import datetime
import io
import json
import requests
import discord
from discord import app_commands
from cmd_gps.classes import constantes
from PIL import Image, ImageFont, ImageDraw
from typing import Optional

class Lista:
    def __init__(self):
        self.value = []

lista = Lista()

def has_manage_roles_or_specific_role():
    def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.manage_roles:
            return True
        
        specific_role_id = constantes.CARGOS.CARGOS_DE_PROMOCAO[-2]
        if any(role.id == specific_role_id for role in interaction.user.roles):
            return True
        
        return False

    return app_commands.check(predicate)

async def pegar_imagem(cargo: discord.Role, promoveu: bool=True):
    with open("imagens_staff.json", "r") as f:
        imagens = json.load(f)
    return imagens[str(cargo.id)][promoveu]

class ComandosStaff(app_commands.Group):
    def __init__(self, bot: discord.Client, lista_: list[app_commands.Choice[str]], cargos_de_promocao: list[int]):
        global lista
        super().__init__(description="Comandos relacionados a staff")
        self.bot = bot
        lista.value = lista_
        self.cargos_de_promocao = cargos_de_promocao

    @app_commands.command(name="form_setup", description="Configura o formulário")
    @app_commands.checks.has_permissions(administrator=True)
    async def form_setup(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(url=constantes.GERAL.FORMULARIO,style=discord.ButtonStyle.link, label="Form Staff", emoji="<:staff:1330635861007798483>"))
        embeds = [
            discord.Embed(
                title="Formulário para Staff",
                description="Junte-se à nossa equipe de moderadores! \nUma comunidade de sucesso começa com uma boa moderação. Se você é responsável, tem bom senso e deseja contribuir, inscreva-se para fazer parte do nosso time!",
                colour=discord.Color.from_str("#0000ff")
            )
        ]
        for i, embed in enumerate(embeds):
            embed.set_thumbnail(url=view.children[i].emoji.url)
        canal = self.bot.get_channel(constantes.CANAIS.CANAL_FORMS)
        mensagens = canal.history(limit=1)
        async for mensagem in mensagens:
            await mensagem.delete()
        await canal.send(embeds=embeds, view=view)
        await interaction.response.send_message("Formulário configurado com sucesso!", ephemeral=True)

    def aplicar_mascara_circular(self, fundo, imagem_cargo, margem, xy, proporcao):
        quadrado_tamanho = proporcao
        mascara = Image.new("L", (quadrado_tamanho, quadrado_tamanho), 0)
        draw = ImageDraw.Draw(mascara)
        draw.ellipse((0, 0, quadrado_tamanho, quadrado_tamanho), fill=255)

        imagem_cargo_x, imagem_cargo_y = xy
        imagem_cargo = imagem_cargo.crop((
            imagem_cargo_x, imagem_cargo_y,
            imagem_cargo_x + quadrado_tamanho, imagem_cargo_y + quadrado_tamanho
        ))

        quadrado = Image.new("RGBA", (quadrado_tamanho, quadrado_tamanho), (0, 0, 0, 0))
        quadrado.paste(imagem_cargo, (0, 0), imagem_cargo)

        cx, cy = margem
        fundo.paste(quadrado, (cx, cy), mascara)

        return fundo

    #async def promover_setup(lista: list[app_commands.Choice[str]], cargos_de_promocao: list[int]):
    async def imagem_promocao(self, cargo: discord.Role, subiu: bool=True):
        texto = "  Staff"
        if subiu:
            if cargo.id == constantes.CARGOS.CARGOS_DE_PROMOCAO[1]:
                texto = "  Novo\n Staff"
            elif cargo.id == constantes.CARGOS.CARGO_MEMBRO:
                texto = "  Saiu\n da Staff"
            else:
                texto += "\nPromovido"
        else:
            if cargo.id == constantes.CARGOS.CARGO_MEMBRO:
                texto += "\nRemovido"
            else:
                texto = "  Caiu\nde cargo"
        texto+="!"
        imagens = {
            "1288525604228169739": {
                "url": "https://static.wikia.nocookie.net/undertale-determination/images/2/2c/0ddFroggit-0.gif/revision/latest/thumbnail/width/360/height/360?cb=20180731200814&path-prefix=pt-br",
                "resize": (1080, 1080),
                "xy": (0, -100)
            },
            "1324397624236703784": {
                "url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSomF3W4SR6rhzI6PO060y4kVnE3ldztknviR8-ReVhBzgO-CUiQ4bXmDo&s=10",
                "resize": (1440, 2024),
                "xy": (0, -200)
            },
            "1296976143093731388": {
                "url": "https://static.wikia.nocookie.net/liberproeliis/images/8/87/Greater_Dog.png/revision/latest?cb=20170215210545&path-prefix=pt-br",
                "resize": (1440, 1286),
                "xy": (100, -200)
            },
            "1318756933439848448": {
                "url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR-vSvi_koobnBwwsQVPrUvOOoPxhGc_dJ0mw&usqp=CAU",
                "resize": (2880, 1508),
                "xy": (0, -200)
            },
            "1289271096687722586": {
                "url": "https://cdn.discordapp.com/attachments/1329835341645090947/1330226896323088394/frame_30.png?ex=678d35d6&is=678be456&hm=439670092ebf1e5e8c663267eaf95c154c134a01ba97ae45f7a21793f6dd2919&",
                "resize": (2160, 1671),
                "xy": (180, -100)
            },
            "1289271355312967730": {
                "url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR1lsrttsEiPlgpsdodAsEMk170l8vrROTyCFWMLH8kUgiAWy_LAlHyxdM&s=10",
                "resize": (2564, 1440),
                "xy": (400, 0)
            }
        }
        coroa_url = "https://cdn.discordapp.com/attachments/1329835341645090947/1330212365895208960/pngtree-golden-laurel-wreath-with-gold-leaf-for-the-winner-and-champion-png-image_6421662.png?ex=678d284e&is=678bd6ce&hm=ef527d15fe545293e269223af1e0c03db399c591da3608c2b68461c5ce847d88&"
        fundo = Image.new("RGB", (2560, 1440))
        coroa_req = requests.get(coroa_url)
        coroa_req.raise_for_status()
        coroa1 = Image.open(io.BytesIO(coroa_req.content)).convert("RGBA")
        coroa = coroa1.resize((1440, 1440))
        imagem_url = imagens.get(str(cargo.id), {}).get("url")
        response_imagem = requests.get(imagem_url)
        imagem_cargo = Image.open(io.BytesIO(response_imagem.content)).convert("RGBA")
        imagem_cargo = imagem_cargo.resize(imagens.get(str(cargo.id), {}).get("resize"))
        margemx = int(33 * coroa.size[0]/coroa1.size[0])
        margemy = int(40 * coroa.size[0]/coroa1.size[0])
        proporcao = int(293 * coroa.size[0]/coroa1.size[0])
        fundo = self.aplicar_mascara_circular(fundo, imagem_cargo, (margemx, margemy), imagens.get(str(cargo.id), {}).get("xy"), proporcao)
        fundo.paste(coroa, (0, 0), coroa)
        fundo_texto = ImageDraw.Draw(fundo)
        fonte = ImageFont.truetype("determination-mono.ttf", size=250)
        bbox = fundo_texto.textbbox((0, 0), texto, font=fonte)
        #largura_texto = bbox[2] - bbox[0]
        altura_texto = bbox[3] - bbox[1]
        posicao_y = (fundo.size[1] - altura_texto) // 2
        fundo_texto.text((1300, posicao_y), texto, font=fonte, fill="white")
        buffer = io.BytesIO()
        fundo.save(buffer, format="PNG")
        return buffer
    
    @app_commands.command(name="imagens_setup", description="Mostra quais imagens são enviadas em cada promoção")
    async def ver_imagem(self, interaction: discord.Interaction):
        if not interaction.guild or interaction.guild.id != 1288221625732431957:
            return await interaction.response.send_message("Ops... Esse comando não é permitido de ser usado nesse servidor!")
        if interaction.user.id != interaction.guild.owner_id:
            return
        await interaction.response.defer(ephemeral=True)
        canal = self.bot.get_channel(1329835341645090947)
        async with canal.typing():
            for escolha in lista:
                cargo = interaction.guild.get_role(int(escolha.value))
                for promoveu in [True, False]:
                    if not (cargo.id == 1289271355312967730 and not promoveu):
                        buffer = await self.imagem_promocao(cargo, promoveu)
                        buffer.seek(0)
                        await canal.send(file=discord.File(fp=buffer, filename=cargo.name + ".png"))
        imagens = {}
        historico = [mensagem.attachments[0].url async for mensagem in canal.history(limit=11)]
        index=0
        historico.reverse()
        for escolha in lista:
            cargo = interaction.guild.get_role(int(escolha.value))
            imagens[str(cargo.id)] = {}
            for promoveu in [True, False]:
                if not (cargo.id == 1289271355312967730 and not promoveu):
                    imagens[str(cargo.id)][str(promoveu)] = historico[index]
                    index+=1
        with open("imagens_staff.json", "w") as f:
            json.dump(imagens, f)
        await interaction.followup.send("Pronto")
        
    @app_commands.command(name="tabela_promocao", description="Mostra a tabela de tempo de promoção para cada cargo")
    @has_manage_roles_or_specific_role()
    async def tabela_promocao(self, interaction: discord.Interaction):
        tabela = ""
        tempo = {str(self.cargos_de_promocao[cg+1]): datetime.timedelta(weeks=2 ** (cg-1)) for cg in range(len(self.cargos_de_promocao[1:]))}
        for cargo_id, duracao in tempo.items():
            cargo = interaction.guild.get_role(int(cargo_id))
            if cargo:
                tabela += f"**{cargo.name}:** {duracao.days // 7} semanas\n"
            else:
                tabela += f"**Cargo com ID {cargo_id}:** {duracao.days // 7} semanas\n"
        await interaction.response.send_message(f"A tabela de tempo de promoção é:\n{tabela}", ephemeral=True)
    
    async def promover_act(self, interaction: discord.Interaction, membro: discord.Member, cargo: discord.Role, motivo: str):
        canal = interaction.guild.get_channel(constantes.CANAIS.CANAL_STAFF_UPDATES)
        role = interaction.guild.get_role(int(cargo))
        wd_gaster = interaction.guild.get_role(constantes.CARGOS.CARGO_EXSTAFF)
        try:
            embed = discord.Embed()

            if isinstance(motivo, str):
                if motivo.lower().startswith("saiu"):
                    embed.colour = discord.Color.blurple()
                    embed.description = motivo[5].capitalize()
                    embed.set_image(url=pegar_imagem(role, False))
                    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
                    for cg in self.cargos_de_promocao:
                        if cg in membro.roles:
                            membro.remove_roles(cg)
                    embed.set_thumbnail(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)
                    await membro.add_roles(interaction.guild.get_role(constantes.CARGOS.CARGO_MEMBRO))
                    await membro.add_roles(wd_gaster)
                    await canal.send(content=membro.mention, embed=embed)
                    try:
                        await interaction.followup.edit_message(embed=embed)
                    except Exception as e:
                        del e
                        await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
            novo_staff_id = constantes.CARGOS.CARGO_STAFF
            promoveu=True

            current_promotion_roles = [cg.id for cg in membro.roles if cg.id in self.cargos_de_promocao]

            if any(cg == int(cargo) for cg in current_promotion_roles):
                await interaction.response.send_message(
                    f"Usuário já tem o cargo {role.mention}.", ephemeral=True
                )
                return
            if constantes.CARGOS.CARGO_MEMBRO in current_promotion_roles:
                new_role = interaction.guild.get_role(novo_staff_id)
                await membro.add_roles(new_role)
                await membro.add_roles(role)
                embed.title="Novo Staff!"
                embed.description = f"{membro.mention} **Aceito a staff** com o cargo <@&{cargo}>!"
                embed.colour = discord.Color.green()
                embed.add_field(name="Aceito por: ", value=interaction.user.mention)
                await membro.remove_roles(interaction.guild.get_role(constantes.CARGOS.CARGO_MEMBRO))
            else:
                current_highest_role = max(
                    (interaction.guild.get_role(role_id) for role_id in current_promotion_roles),
                    key=lambda r: r.position
                )
                new_role = interaction.guild.get_role(int(cargo))
                embed.add_field(name="Cargo anterior", value=current_highest_role.mention)
                if new_role.position > current_highest_role.position:
                    await membro.add_roles(new_role)
                    embed.title = "Staff promovido!"
                    embed.description = f"{membro.mention} foi promovido ao cargo {new_role.mention}!"
                    embed.colour = discord.Color.green()
                    embed.add_field(name="Promovido por: ", value=interaction.user.mention)
                    for cg in current_promotion_roles:
                        cg = interaction.guild.get_role(cg)
                        try:
                            await membro.remove_roles(cg)
                        except Exception as e:
                            del e
                            print(f"Erro ao remover {cg.mention}")
                elif new_role.id == constantes.CARGOS.CARGO_MEMBRO:
                    for cg in current_promotion_roles:
                        cg = interaction.guild.get_role(cg)
                        try:
                            await membro.remove_roles(cg)
                        except Exception as e:
                            del e
                            print(f"Erro ao remover {cg.mention}")
                    await membro.remove_roles(interaction.guild.get_role(novo_staff_id))
                    await membro.add_roles(interaction.guild.get_role(constantes.CARGOS.CARGO_MEMBRO))
                    await membro.add_roles(wd_gaster)
                    promoveu = False
                    embed.title = "Staff removido!"
                    embed.description = f"{membro.mention} foi **Removido da staff**!"
                    embed.colour = discord.Color.from_str("#ff0000")
                    embed.add_field(name="Removido por: ", value=interaction.user.mention)
                else:
                    for cg in current_promotion_roles:
                        cg = interaction.guild.get_role(cg)
                        try:
                            await membro.remove_roles(cg)
                        except Exception as e:
                            del e
                            print(f"Erro ao remover {cg.mention}")
                    await membro.add_roles(new_role)
                    promoveu = False
                    embed.title = "Desceu de cargo."
                    embed.description = f"{membro.mention} foi **rebaixado** ao cargo {new_role.mention}."
                    embed.colour = discord.Color.orange()
                    embed.add_field(name="Rebaixado por: ", value=interaction.user.mention)
            embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
            url = await pegar_imagem(role, str(promoveu))
            embed.set_image(url=url)
            embed.set_thumbnail(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)
            embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            if motivo:
                embed.add_field(name="Motivo", value=motivo)
            await canal.send(content=membro.mention, embed=embed)
            if motivo != "Convidado":
                try:
                    await interaction.response.edit_message(content="", view=None, embed=embed)
                except Exception as e:
                    del e
                    await interaction.followup.send(content="", view=None, embed=embed)
        except discord.Forbidden:
            await interaction.followup.send(
                "Eu não tenho permissão para gerenciar esses cargos.", ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"Ocorreu um erro ao tentar promover o membro: {e}"
                )

    class PromoverAgora(discord.ui.View):
        def __init__(self, interaction: discord.Interaction, membro: discord.Member, cargo: int, motivo: str, cmd_staff):
            super().__init__(timeout=60)
            self.interaction = interaction
            self.membro = membro
            self.cargo = cargo
            self.motivo = motivo
            self.cmd_staff: ComandosStaff = cmd_staff

        @discord.ui.button(label="Promover agora", style=discord.ButtonStyle.green)
        async def promover_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.cmd_staff.promover_act(interaction=interaction, membro=self.membro, cargo=self.cargo, motivo=self.motivo)

    async def ver_tempo_staff(self, staff: discord.Member, cargo: discord.Role) -> tuple[Optional[datetime.datetime], Optional[datetime.timedelta], Optional[datetime.timedelta], datetime.timedelta]:
        current_promotion_roles = [cg.id for cg in staff.roles if cg.id in self.cargos_de_promocao]

        canal = self.bot.get_channel(constantes.CANAIS.CANAL_STAFF_UPDATES)

        mensagens = [msg async for msg in canal.history(limit=100)]
        ultima_promocao = None

        for mensagem in mensagens:
            if str(staff.id) in mensagem.content and mensagem.embeds[0].colour == discord.Color.green():
                ultima_promocao = mensagem.created_at
                break

        tempo = {
            str(self.cargos_de_promocao[cg+1]): datetime.timedelta(weeks=2 ** cg) for cg in range(len(self.cargos_de_promocao)-1)
        }
        cargo_atual = max(
            (staff.guild.get_role(role_id) for role_id in current_promotion_roles),
            key=lambda r: r.position
        )
        indice_cargo_atual = self.cargos_de_promocao.index(cargo_atual.id)

        tempo_minimo=sum(
            (
                tempo[str(cargo_)] if str(cargo_) in tempo else datetime.timedelta(days=0)
                for cargo_ in self.cargos_de_promocao[indice_cargo_atual:self.cargos_de_promocao.index(cargo.id)]
            ),
            datetime.timedelta()
        )
        
        if ultima_promocao:
            agora = datetime.datetime.now(datetime.timezone.utc)
            tempo_desde_ultima = agora - ultima_promocao
            tempo_falta = tempo_minimo - tempo_desde_ultima
            return (ultima_promocao, tempo_falta, tempo_desde_ultima, tempo_minimo)
        
        return (None, None, None, tempo_minimo)

    @app_commands.command(name="promover", description="Promove um membro a staff")
    @app_commands.describe(
        membro="O membro que será promovido",
        cargo="Qual cargo será dado ao membro",
        motivo="O motivo da promoção (Apenas remoção, saída e rebaixamento)"
    )
    @app_commands.choices(
        cargo=lista.value
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def promover(self, interaction: discord.Interaction, membro: discord.Member, cargo: str, motivo: str=None):
        role = interaction.guild.get_role(int(cargo))
        
        if role is None:
            await interaction.response.send_message("O cargo selecionado não é válido.", ephemeral=True)
            return

        if interaction.user == membro:
            await interaction.response.send_message("Você não pode se promover!", ephemeral=True)
            return

        if interaction.user.top_role <= role and interaction.user.id != interaction.guild.owner.id:
            await interaction.response.send_message("Você não pode promover alguém a um cargo igual ou maior que o seu.", ephemeral=True)
            return
        
        if membro.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner.id:
            await interaction.response.send_message("Você não pode promover este membro pois ele possui um cargo igual ou maior que o seu.", ephemeral=True)
            return
        
        current_promotion_roles = [cg.id for cg in membro.roles if cg.id in self.cargos_de_promocao]

        if any(cg == int(cargo) for cg in current_promotion_roles):
            await interaction.response.send_message(
                f"Usuário já tem o cargo {role.mention}.", ephemeral=True
            )
            return
        if constantes.CARGOS.CARGO_MEMBRO in current_promotion_roles and constantes.CARGOS.CARGO_MEMBRO == role.id:
            await interaction.response.send_message("Ele não é da staff para ser removido da staff", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)

        ultima_promocao, tempo_falta, tempo_desde_ultima, tempo_minimo = await self.ver_tempo_staff(staff=membro, cargo=role)

        if tempo_falta:
            agora = datetime.datetime.now(datetime.timezone.utc)
            if tempo_desde_ultima < tempo_minimo:
                timestamp_falta = (agora + tempo_falta).timestamp()
                return await interaction.followup.send(f"Olha, {interaction.user.mention}, o {membro.mention} foi promovido <t:{int(ultima_promocao.timestamp())}:R>. Recomendo promover <t:{int(timestamp_falta)}:R>. Deseja fazer isso agora?", view=self.PromoverAgora(interaction, membro, cargo, motivo, self))
        await self.promover_act(interaction, membro, cargo, motivo)
    
    @app_commands.command(name="ver_tempo", description="Ver o tempo restante para promover um membro")
    @has_manage_roles_or_specific_role()
    async def ver_tempo(self, interaction: discord.Interaction, membro: discord.Member):
        await interaction.response.defer(ephemeral=True)
        
        current_promotion_roles = [cg.id for cg in membro.roles if cg.id in self.cargos_de_promocao and cg.id != self.cargos_de_promocao[0]]

        if any(cg.id == constantes.CARGOS.CARGO_DONOS for cg in membro.roles):
            await interaction.followup.send(f"{membro.mention} já é dono kkkkk.", ephemeral=True)
            return
        
        if not current_promotion_roles:
            await interaction.followup.send(f"{membro.mention} não é da staff")
            return
        
        if any(cg.id == self.cargos_de_promocao[-1] for cg in membro.roles):
            await interaction.followup.send("Ele já está no cargo máximo.", ephemeral=True)
            return

        role = max(
            (interaction.guild.get_role(role_id) for role_id in current_promotion_roles),
            key=lambda r: r.position
        )

        for i in self.cargos_de_promocao:
            if i == role.id:
                index = self.cargos_de_promocao.index(i)+1
        
        role = interaction.guild.get_role(self.cargos_de_promocao[index])
        
        ultima_promocao, tempo_falta, tempo_desde_ultima, tempo_minimo = await self.ver_tempo_staff(staff=membro, cargo=role)

        if ultima_promocao:
            agora = datetime.datetime.now(datetime.timezone.utc)
            timestamp_falta = (agora + tempo_falta).timestamp()
            if tempo_desde_ultima < tempo_minimo:
                await interaction.followup.send(f"{membro.mention} foi promovido <t:{int(ultima_promocao.timestamp())}:R>. Recomendo promover <t:{int(timestamp_falta)}:R>.")
                return
            await interaction.followup.send(f"{membro.mention} foi promovido <t:{int(ultima_promocao.timestamp())}:R>. Ele deveria ter sido promovido <t:{int(timestamp_falta)}:R>.")
            return
        await interaction.followup.send("Ele ainda não foi promovido")
    
    lista_local = lista.copy()
    lista_local.append(app_commands.Choice(name=constantes.CARGOS.CARGO_DONOS_NOME, value=str(constantes.CARGOS.CARGO_DONOS)))
    lista_local.pop(0)
    
    class ConviteView(discord.ui.View):
        def __init__(self, precisa_form: bool, membro: discord.Member, interaction: discord.Interaction, cmd_staff):
            super().__init__(timeout=None)
            self.precisa_form = precisa_form
            self.membro = membro
            self.interaction = interaction
            self.cmd_staff: ComandosStaff = cmd_staff
    
            if precisa_form:
                self.add_item(discord.ui.Button(label="Preencher Formulário", url=constantes.FORMULARIO, style=discord.ButtonStyle.link))
            else:
                self.add_item(self.cmd_staff.PromoverButton(membro, interaction, cmd_staff))
    
    class PromoverButton(discord.ui.Button):
        def __init__(self, membro: discord.Member, interaction: discord.Interaction, cmd_staff):
            super().__init__(label="Aceitar na Staff", style=discord.ButtonStyle.success)
            self.membro = membro
            self.interaction = interaction
            self.cmd_staff: ComandosStaff = cmd_staff
    
        async def callback(self, interaction: discord.Interaction):
            await self.cmd_staff.promover_act(interaction=self.interaction, membro=self.membro, cargo=constantes.CARGOS.CARGOS_DE_PROMOCAO[1], motivo="Convidado")
            await interaction.response.edit_message(content=f"{self.membro.mention} foi promovido para a staff!", view=None)
    
    @app_commands.command(name="convidar", description="Convide um membro para a staff")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def convidar(self, interaction: discord.Interaction, membro: discord.Member, precisa_form: bool, texto: str = None):
        texto = texto or (
            f"Olá! Você foi convidado para fazer parte da staff do {interaction.guild.name}!\n\n"
            f"Você {'precisa' if precisa_form else 'não precisa'} preencher um formulário para ser aceito.\n\n"
            "O que acha? Clique no botão abaixo para continuar."
        )
        view = self.ConviteView(precisa_form, membro, interaction, self)
        embed = discord.Embed(
            title="Convite para a staff!!",
            description=texto,
            colour=interaction.user.color
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
        embed.set_thumbnail(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)
        try:
            await membro.send(embed=embed, view=view)
            await interaction.response.send_message(f"Convite enviado para {membro.mention}!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"Não foi possível enviar a mensagem para {membro.mention}.", ephemeral=True)
    
    @app_commands.command(name="staffs", description="Veja as informações da equipe staff!")
    @app_commands.choices(
        cargo=lista_local
    )
    async def staffs(self, interaction: discord.Interaction, cargo: str = None):
        embed = discord.Embed(title="Membros da equipe", colour=discord.Color.from_str("#ff0000"))
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
        if cargo:
            staff_role = interaction.guild.get_role(int(cargo))
            staffs = [staff.mention for staff in staff_role.members]
            embed.add_field(name=f"{staff_role.name.title()} - {len(staffs)}", value=" ".join(staffs))
        else:
            staff_role = interaction.guild.get_role(constantes.CARGOS.CARGO_STAFF)
            staffs = [staff.mention for staff in staff_role.members]
            embed.add_field(name=f"Staffs totais - {len(staffs)}", value=" ".join(staffs))
            for cargo in self.cargos_de_promocao[1:]:
                staff_role = interaction.guild.get_role(cargo)
                staffs = [staff.mention for staff in staff_role.members]
                embed.add_field(name=f"{staff_role.name.title()} - {len(staffs)}", value=" ".join(staffs))
            tobyfox = interaction.guild.get_role(constantes.CARGOS.CARGO_DONOS)
            embed.add_field(name=f"{constantes.CARGOS.CARGO_DONOS_NOME} - {len(tobyfox.members)}", value=" ".join([staff.mention for staff in tobyfox.members]))
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="mensagens_staff", description="Boas-vindas, staffs!")
    @app_commands.choices(
        cargo=lista_local
    )
    async def msg_staff(self, interaction: discord.Interaction, cargo: str):
        embed = discord.Embed(colour=interaction.guild.get_role(int(cargo)).color)
        textos = {
            constantes.CARGOS.CARGOS_DE_PROMOCAO[1]: {
                "title": "NYEH HEH HEH!!!",
                "description": "FINALMENTE! O MOMENTO QUE TODOS ESTAVAM ESPERANDO! EU, O GRANDE PAPYRUS, FUI PROMOVIDO PARA A STAFF!!!\nAGORA, COMO UM MEMBRO ORGULHOSO DA EQUIPE, MEU PRIMEIRO DEVER É... HUM... OBSERVAR E AJUDAR COM PEQUENAS TAREFAS? BEM, CLARO! TODO GRANDE HERÓI COMEÇA COM PASSOS PEQUENOS! ATÉ MESMO OS MAIORES GUERREIROS PRECISAM TREINAR PRIMEIRO!\nCOM O TEMPO, PROVAREI MEU VALOR, SUBIREI DE constantes.CARGOS.CARGO E ME TORNAREI UMA FIGURA LENDÁRIA NESTE SERVIDOR! E QUANDO ISSO ACONTECER, SERÁ UM DIA MEMORÁVEL PARA TODOS!\nMAS ATÉ LÁ... VOU ME CERTIFICAR DE QUE ESTE SERVIDOR SEJA UM LUGAR AGRADÁVEL E JUSTO PARA TODOS! POIS, ACIMA DE TUDO, EU SOU UM GUARDA REAL MUITO FAMOSO\nNYEH HEH HEH!!!\n\nNota: AINDA NÃO É UM GUARDA REAL MUITO FAMOSO."
            },
            constantes.CARGOS.CARGOS_DE_PROMOCAO[2]: {
                "title": "Huh?! Eu... EU FUI PROMOVIDO?!?",
                "description": "Isso é incrível! Agora tenho um cargo de extrema importância...\nMas espere... O que exatamente eu faço?\n...\nHã? Minha função é mutar usuários, aplicar warns e acessar tickets?\nCERTO! ENTENDIDO! Ninguém vai causar problemas... quer dizer, nenhuma infração passará despercebida enquanto eu estiver aqui!!!\n...\nEi, aquele usuário ali... Parece estar causando confusão.\nWARNADO!\nAquele outro ali passou dos limites...\nMUTADO!\n\nEspera... Se ninguém está falando, como vão saber que estou fazendo um bom trabalho?!?\n...\nPRECISO DE PETISCOS PARA CACHORRO PARA PENSAR SOBRE ISSO."
            }
        }
        embed.title=textos[cargo]["title"]
        embed.description=textos[cargo]["description"]
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ticket_treinamento", description="Abra um ticket de treinamento")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_treina(self, interaction: discord.Interaction):
        canal_existente = discord.utils.get(interaction.guild.text_channels, name="treina " + str(interaction.user.id))
                
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

            canal_silent = await interaction.guild.create_text_channel(
                name="treina " + str(interaction.user.id),
                category=interaction.guild.get_channel(constantes.CATEGORIAS.CATEGORIA_TICKETS),
                overwrites=overwrites
            )
            silent_embed = discord.Embed(
                title="Ticket de Treinamento",
                colour=discord.Color.green(),
                description=(
                    "Este é o seu **ticket de trejnamento**, criado para treinar outros staffs.\n\n"
                    "Apenas você e os cargos autorizados têm acesso a este canal. "
                )
            )
            silent_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            from .classes import TicketView
            await canal_silent.send(embed=silent_embed,
            view=TicketView(bot=self.bot), content=f"{interaction.user.mention}")
            embed = discord.Embed(
                title="Ticket criado!",
                colour=discord.Color.from_str("#fe0000"),
                description=(
                    "Seu **ticket de treinamento** foi criado com sucesso!\n"
                    "Use o botão abaixo para acessar o canal privado onde você pode ajudar a outros staffs."
                )
            )
            view = discord.ui.View()
            link = discord.ui.Button(label="Ver ticket", url=f"https://discord.com/channels/{constantes.CAREGORIA.CATEGORIA_TICKETS}/{canal_silent.id}", style=discord.ButtonStyle.link)
            view.add_item(link)
            await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
    
    @app_commands.command(name="avaliar", description="Avalie um treinamento!")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        staff="Membro da equipe que será avaliado",
        tipo="Tipo de treinamento",
        nota="Nota do treinamento (0 a 10)",
        oq_falta="O que faltou para atingir 10 (opcional)"
    )
    async def avaliar(self, interaction: discord.Interaction, staff: discord.Member, tipo: str, nota: int, oq_falta: str = None):
        if nota < 0 or nota > 10:
            await interaction.response.send_message("A nota deve estar entre 0 e 10.", ephemeral=True)
            return

        if nota >= 7:
            descricao = "Boa nota! Continue assim."
            cor = discord.Color.from_str("#00ff00")
        elif 5 <= nota < 7:
            descricao = "Pode melhorar, mas está bom."
            cor = discord.Color.orange()
        else:
            descricao = "Sem comentários."
            cor = discord.Color.from_str("#ff0000")

        embed = discord.Embed(
            title="Nota do treinamento",
            description=descricao,
            color=cor
        )
        embed.add_field(name="Nota:", value=f"`{nota}/10`", inline=False)
        embed.add_field(name="Tipo de treinamento:", value=tipo, inline=False)

        if oq_falta and nota < 10:
            embed.add_field(name="O que faltou para 10?", value=oq_falta, inline=False)
            
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
        embed.set_thumbnail(url=staff.avatar.url if staff.avatar else staff.default_avatar.url)
        canal = interaction.client.get_channel(constantes.CANAIS.CANAL_AVALIACAO)
        if canal:
            await canal.send(content=staff.mention, embed=embed)
            await interaction.response.send_message("Avaliação enviada com sucesso!", ephemeral=True)
        else:
            await interaction.response.send_message("Não consegui encontrar o canal para enviar a avaliação.", ephemeral=True)
            
    @avaliar.autocomplete("tipo")
    async def tipo_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
        tipos = ["Denúncia simples", "Denúcia grave", "Parceria", "Denúncia falsa", "Falsa acusação"]
        
        sugestões = [app_commands.Choice(name=tipo, value=tipo) for tipo in tipos if current.lower() in tipo.lower()]
        return sugestões[:25]

    @app_commands.command(name="ticket_silencioso", description="Abra um ticket silencioso")
    async def ticket_silent(self, interaction: discord.Interaction):
        if interaction.guild.get_role(constantes.CARGOS.CARGO_DONOS) not in interaction.user.roles:
            await interaction.response.send_message("Você não tem autorização de executar esse comando.", ephemeral=True)
        canal_existente = discord.utils.get(interaction.guild.text_channels, name="silent " + str(interaction.user.id))
                
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

            canal_silent = await interaction.guild.create_text_channel(
                name="silent " + str(interaction.user.id),
                category=interaction.guild.get_channel(constantes.CATEGORIAS.CATEGORIA_TICKETS),
                overwrites=overwrites
            )
            silent_embed = discord.Embed(
                title="Ticket Silencioso",
                colour=discord.Color.green(),
                description=(
                    "Este é o seu **ticket silencioso**, criado para tratar de assuntos confidenciais.\n\n"
                    "Apenas você e os cargos autorizados têm acesso a este canal. "
                )
            )
            silent_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            from .classes import TicketView
            await canal_silent.send(embed=silent_embed,
            view=TicketView(bot=self.bot), content=f"{interaction.user.mention}")
            embed = discord.Embed(
                title="Ticket criado!",
                colour=discord.Color.from_str("#ff0000"),
                description=(
                    "Seu **ticket silencioso** foi criado com sucesso!\n"
                    "Use o botão abaixo para acessar o canal privado onde você pode resolver brigas e treinar staffs.."
                )
            )
            view = discord.ui.View()
            link = discord.ui.Button(label="Ver ticket", url=f"https://discord.com/channels/{constantes.CATEGORIAS.CATEGORIA_TICKETS}/{canal_silent.id}", style=discord.ButtonStyle.link)
            view.add_item(link)
            await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
