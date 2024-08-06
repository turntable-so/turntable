type FeatureFlags = {
    notebookTabExp: boolean
}
export default function getFeatureFlags(tenantId: string): FeatureFlags {

    return {
        notebookTabExp: tenantId === 'org_2XVt0EheumDcoCerhQzcUlVmXvG'
    }
}