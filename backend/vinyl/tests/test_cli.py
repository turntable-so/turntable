from vinyl.lib.utils.files import _get_changed_files


def test_generate_sources():
    @_get_changed_files("internal_project/sources")
    def test():
        import vinyl.cli.sources as sources_cli

        sources_cli.generate_sources(twin=False, resources=["local_filesystem"])

    assert test() == {}


def test_preview_model():
    import vinyl.cli.preview as preview_cli

    preview_cli.preview_model(name="amount_base", twin=False, shutdown_seconds=1)

    assert True


def test_preview_metric():
    import vinyl.cli.preview as preview_cli

    preview_cli.preview_metric(name="fare_metrics", grain="days=1", shutdown_seconds=1)

    assert True
