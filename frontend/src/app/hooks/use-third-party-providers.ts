export const useThirdPartyProviders = () => {
  const providers = [
    { type: "OpenAI", credentials: [{ name: "API Key" }] },
    {
      type: "Anthropic",
      credentials: [{ name: "Account ID" }, { name: "API Secret" }],
    },
  ];

  return { providers };
};
