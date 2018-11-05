import click

from . import bootstrap


class CLI(click.MultiCommand):

    def list_commands(self, ctx):
        return sorted(self.cmds.keys())

    def get_command(self, ctx, cmd_name):
        try:
            return self.cmds[cmd_name]
        except KeyError:
            raise click.UsageError(click.style(
                "cmd not exist: {}\nAvailable ones are: {}".format(
                    cmd_name, ', '.join(self.cmds),
                ), fg='red'))

    @property
    def cmds(self):
        return {func.name: func for func in bootstrap.CMDS}


@click.command(cls=CLI)
@click.version_option()
@click.option('--echo/--no-echo', default=False, help='Show cmd run msg.')
@click.pass_context
def main(ctx, echo):
    if ctx.obj is None:
        ctx.obj = dict()
    ctx.obj['ECHO'] = echo


if __name__ == '__main__':
    main()
