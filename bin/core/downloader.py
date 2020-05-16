@client.command(pass_context=True, aliases=['wr', 'wa'])
async def warn(ctx):
    author = ctx.guild.get_member(int(ctx [4:22]))
    file = openpyxl.load_workbook("./bin/user_data/user_warn.xlsx")
    sheet = file.active

    i =1
    while True:
        if sheet["A" + str(i)].value == str(ctx.author.id):
            sheet["B" + str(i)].value = int(sheet["B" + str(i)].value) + 1
            file.save("./bin/user_data/user_warn.xlsx")
            if sheet["B" + str(i)].value == 2:
                await ctx.guild.ban(author)
                await ctx.channel.send("You Have Been Banned")
            else:
                await ctx.send("You Get The Warn.")
        if sheet["A" + str(i)].value == None:
            sheet["A" + str(i)].value = str(ctx.author.id)
            sheet["B" + str(i)].value = 1
            file.save("./bin/user_data/user_warn.xlsx")
            await ctx.send("You Get The Warn.")
        i += 1
