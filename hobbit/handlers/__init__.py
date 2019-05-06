import click


@click.pass_context
def echo(ctx, msg, args=None):
    if not ctx.obj['ECHO']:
        return

    if args:
        click.echo(msg.format(*args))
    else:
        click.echo(msg)
