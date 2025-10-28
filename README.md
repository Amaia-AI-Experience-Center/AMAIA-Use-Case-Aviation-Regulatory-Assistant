# AMAIA Use Case: Aviation Regulatory Assistant

## Descripción

Este proyecto implementa un sistema multi-agente de consulta de normativas aeronáuticas utilizando el SDK de Azure AI Agents. El sistema permite orquestar consultas a diferentes normativas especializadas mediante una arquitectura de agentes conectados.

Este caso de uso demuestra el uso de Connected Agent Tools para crear arquitecturas multi-agente que consultan inteligentemente diferentes fuentes de conocimiento especializado basándose en el contexto de la pregunta del usuario.

### Arquitectura
```
Consulta del usuario
    ↓
[Agente Orquestador]
    ├→ [EASA] → Consultado si se menciona
    ├→ [DEF-STAN] → Consultado si se menciona
    ├→ [EDA] → Consultado si se menciona
    ├→ [FAA] → Consultado si se menciona
    └→ [JSSG] → Consultado si se menciona
    ↓
Respuesta integral verificada
```
