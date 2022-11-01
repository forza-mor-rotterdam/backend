from signals.apps.signals import workflow

MSB_NIEUW = "Nieuw"
MSB_INBEHANDELING = "Inbehandeling"
MSB_DOORVERWEZEN = "Doorverwezen gekregen"
MSB_HEROPEND = "Heropend"

MSB_TO_SIGNALS_STATE = {
    MSB_NIEUW: workflow.GEMELD,
    MSB_INBEHANDELING: workflow.BEHANDELING,
    MSB_DOORVERWEZEN: workflow.VERZOEK_TOT_AFHANDELING,
    MSB_HEROPEND: workflow.HEROPEND,
}