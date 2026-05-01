// PubCast AI — avatar.js
// Compatibility shim added during the no-user-needed audit pass.
// dressing_foundry.html still includes /static/avatar.js as a classic script,
// while the actual holographic implementation now lives in avatar_glow.js as
// an ES module. This shim bridges that gap without rewriting the page.
(function () {
  async function loadAvatarModule() {
    try {
      const mod = await import('/static/avatar_glow.js');
      if (mod?.HolographicAvatarSystem) {
        window.HolographicAvatarSystem = mod.HolographicAvatarSystem;
      }
      if (mod?.default && !window.HolographicAvatarSystem) {
        window.HolographicAvatarSystem = mod.default;
      }
      window.__pubcastAvatarModuleReady = true;
    } catch (error) {
      window.__pubcastAvatarModuleReady = false;
      console.warn('PubCast avatar compatibility shim failed to load avatar_glow.js', error);
    }
  }

  loadAvatarModule();
})();
