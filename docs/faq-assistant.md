# FAQ assistant preview

The assistant reads `/content/faq.json`, the same static content source as the FAQ page. Seven sidebar buttons match published questions by their full title in `static/js/faq-assistant.js`. Four starter cards also point to these same FAQ entries. Clicking one displays that FAQ's answer, category note, and sources. Editing the FAQ answer and rebuilding the site updates the assistant. When renaming a selected FAQ question, also update its title in `SUGGESTIONS`; array order does not matter.

Typed questions always receive the coming-soon notice, including text that matches a suggestion. They are rendered as plain text and are not sent to an API or stored by the assistant. This page does not call `/api/ai-assistant`. Existing backend AI code is not used by this interface.

The model selector is a display-only preview. Public API availability was checked against official documentation on 14 September 2026. These are feasible integration candidates, not a claim about which model is newest or clinically validated:

- [OpenAI GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini): `gpt-5.4-mini`.
- [Anthropic Claude Sonnet 4.6](https://platform.claude.com/docs/en/models/sonnet-4-6/overview): `claude-sonnet-4-6` (active legacy model).
- [xAI Grok 4.6](https://docs.x.ai/developers/models): `grok-4.6`.

Selecting a model updates its provider description only. It does not enable generation or change FAQ responses. API keys belong to provider developer accounts; access and billing must be checked before integration. Keys must never be placed in static HTML, JavaScript or the exported `dist` directory. Recheck availability and evaluate grounded answers before a future integration.

“New chat” clears the current in-memory conversation, restores the starter cards and retains the preview model choice. It makes no network request and stores no history. The FAQ loading error remains recoverable through “Try again” in the sidebar/mobile drawer.

Run the behavior checks from the project root:

```sh
node --test tests/faq-assistant.test.cjs
```

Also check the page at desktop and mobile widths: click each question and starter card, open its further-reading links, submit a typed question, change the preview model and start a new chat. On mobile, all seven questions and the model previews are available through “Suggested questions & models”.
