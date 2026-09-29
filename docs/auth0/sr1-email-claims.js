/** Deploy as an Auth0 post-login Action and add it to the Login flow. */
exports.onExecutePostLogin = async (event, api) => {
  const namespace = 'https://smartrisk.fotonconsulting.com/';
  if (event.user.email) {
    api.accessToken.setCustomClaim(namespace + 'email', event.user.email);
    api.accessToken.setCustomClaim(namespace + 'email_verified', event.user.email_verified === true);
  }
};
