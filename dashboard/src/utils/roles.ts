
export const isSystemManager = () => {
    //@ts-expect-error expected
    return (window?.frappe?.boot?.user?.roles ?? []).includes('System Manager');
}