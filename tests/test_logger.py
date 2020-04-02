import pytest

from nuage_metroae_config.logger import Logger

LOGGING_CASES = ["LOG", "ERROR", "OUTPUT", "DEBUG"]


class TestLogger(object):

    @pytest.mark.parametrize("log_type", LOGGING_CASES)
    def test_log__single(self, log_type, capsys):
        logger = Logger()
        logger.set_to_stdout(log_type, False)

        getattr(logger, log_type.lower())("No stdout")

        logger.set_to_stdout(log_type, True)

        getattr(logger, log_type.lower())("Yes stdout")

        out, err = capsys.readouterr()

        assert "No stdout" not in out
        assert "Yes stdout" in out

        log = logger.get()

        assert log_type + ": No stdout" in log
        assert log_type + ": Yes stdout" in log

    @pytest.mark.parametrize("log_type", LOGGING_CASES)
    def test_log__multiple(self, log_type, capsys):
        logger = Logger()
        logger.set_to_stdout(log_type, False)

        getattr(logger, log_type.lower())("No stdout\nnext line 1")

        logger.set_to_stdout(log_type, True)

        getattr(logger, log_type.lower())("Yes stdout\nnext line 2")

        out, err = capsys.readouterr()

        assert "No stdout" not in out
        assert "next line 1" not in out
        assert "Yes stdout" in out
        assert "next line 2" in out

        log = logger.get()

        assert log_type + ": No stdout" in log
        assert log_type + ": next line 1" in log
        assert log_type + ": Yes stdout" in log
        assert log_type + ": next line 2" in log
