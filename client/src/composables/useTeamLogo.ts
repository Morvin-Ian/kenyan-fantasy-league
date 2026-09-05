import { computed, ref } from 'vue';
import { useKplStore } from '@/stores/kpl';

/**
 * Club badges are served from our own media, not from the upstream source the
 * scraper downloads them from. The API field is `logo`; a club that has not had
 * its badge cached yet returns null, and callers fall back to the placeholder.
 */

function createPlaceholderLogo(): string {
    const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="45" fill="#e5e7eb"/>
      <path d="M50 30 L70 60 L50 55 L30 60 Z" fill="#9ca3af"/>
    </svg>
  `;
    return `data:image/svg+xml;base64,${btoa(svg)}`;
}

export const PLACEHOLDER_LOGO = createPlaceholderLogo();

/** Badge for a club id, from whichever loaded collection knows about it. */
export function getTeamLogo(teamId: string): string {
    const kplStore = useKplStore();
    const standing = kplStore.standings.find(s => s.team.id === teamId);
    return standing?.team.logo || PLACEHOLDER_LOGO;
}

export function getTeamLogoFromStandings(teamIdOrName: string, standings: any[]): string {
    const standing = standings.find(
        s => s.team.id === teamIdOrName || s.team.name === teamIdOrName
    );
    return standing?.team.logo || PLACEHOLDER_LOGO;
}

export function useTeamLogo(teamId: string, initialLogo?: string | null) {
    const hasError = ref(false);

    const logoUrl = computed(() => {
        if (hasError.value) {
            return PLACEHOLDER_LOGO;
        }
        return initialLogo || getTeamLogo(teamId);
    });

    // Our own media 404s only if the badge was never cached; there is no second
    // URL worth retrying, so drop straight to the placeholder.
    const handleError = () => {
        hasError.value = true;
    };

    const resetError = () => {
        hasError.value = false;
    };

    return { logoUrl, handleError, resetError, hasError };
}
