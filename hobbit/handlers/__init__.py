import click


@click.pass_context
def echo(ctx, msg):
    if not ctx.obj['ECHO']:
        return
    click.echo(msg)
