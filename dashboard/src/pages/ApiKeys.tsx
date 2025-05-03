import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label"
import { Copy, RefreshCw } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { toast } from "sonner";
import { useFrappeGetCall, useSWRConfig } from "frappe-react-sdk";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { useContext, useState } from "react";
import { UserContext } from "@/providers/UserProvider";

export const ApiKeys = () => {

    const { currentUser } = useContext(UserContext)

    const { data } = useFrappeGetCall<{ message: { api_key: string } }>('frappe.client.get_value', {
        doctype: "User",
        filters: {
            name: currentUser
        },
        fieldname: ["api_key"]
    }, currentUser ? `notification.api_key` : null)

    return (
        <div className="container">
            <h1 className="text-3xl font-bold mb-2">API Keys</h1>
            <p className="text-gray-600">
                To send push notifications, you need to configure your API keys. These credentials
                are required to authenticate your requests to the Raven Cloud service.
            </p>

            <div className="py-6 mb-8">
                <div className="space-y-6">
                    {
                        data?.message?.api_key && (
                            <div>
                                <div className="grid w-full max-w-lg items-center gap-2">
                                    <Label
                                        htmlFor="apiKey"
                                    >
                                        API Key
                                    </Label>
                                    <div className="flex w-full items-center space-x-2">
                                        <Input
                                            id="apiKey"
                                            value={data?.message?.api_key}
                                            readOnly
                                            className="flex-1 bg-gray-50"
                                        />
                                        <Tooltip>
                                            <TooltipTrigger asChild>
                                                <Button
                                                    variant="outline"
                                                    size="icon"
                                                    className="ml-2 transition-colors"
                                                // onClick={() => copyToClipboard(apiKeys?.api_key)}
                                                >
                                                    <Copy className="h-4 w-4" />
                                                </Button>
                                            </TooltipTrigger>
                                            <TooltipContent>
                                                Copy API Key
                                            </TooltipContent>
                                        </Tooltip>
                                    </div>
                                </div>
                            </div>
                        )
                    }

                    <div>
                        <ApiKeysDialog text={data?.message?.api_key ? "Regenerate API Keys" : "Generate API Keys"} />
                    </div>
                </div>
            </div>
        </div>
    )
}


//  Dialog to show the api keys
const ApiKeysDialog = ({ text }: { text: string }) => {

    const { mutate } = useSWRConfig()

    const [open, setOpen] = useState(false)

    useFrappeGetCall("raven_cloud.api.notification.generate_api_keys", undefined,
        open ? undefined : null,
        {
            revalidateOnFocus: false,
            revalidateOnReconnect: false,
            shouldRetryOnError: false,
            onSuccess: (data) => {
                setApiKey(data.message.api_key)
                setApiSecret(data.message.api_secret)
                mutate(`notification.api_key`)
                toast.success("API keys regenerated successfully")
            },
            onError: () => {
                toast.error("Failed to regenerate API keys")
            }
        },
        "POST"
    )

    const [apiKey, setApiKey] = useState<string | null>(null)
    const [apiSecret, setApiSecret] = useState<string | null>(null)

    // Copy functionality with visual feedback
    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text)
        toast.success("Copied to clipboard")
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="default">
                    <RefreshCw className="h-4 w-4" />
                    {text}
                </Button>
            </DialogTrigger>

            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Your API Keys</DialogTitle>
                    <DialogDescription>
                        <div className="bg-slate-50 border border-slate-200 rounded-md p-3 mt-2 mb-2 text-slate-800">
                            In Raven app, go to <span className="font-semibold">Settings</span> &#62; <span className="font-semibold">Push Notifications</span> &#62; Paste the API Key and API Secret.
                        </div>
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-6 py-2">
                    <div className="space-y-2">
                        <Label htmlFor="apiKey" className="font-medium">API Key</Label>
                        <div className="flex items-center space-x-2">
                            <Input
                                id="apiKey"
                                value={apiKey || ''}
                                readOnly
                                className="font-mono text-sm bg-gray-50"
                            />
                            <Button
                                variant="outline"
                                size="icon"
                                disabled={!apiKey}
                                onClick={() => copyToClipboard(apiKey || "")}
                                title="Copy API Key"
                                className="cursor-default"
                            >
                                <Copy className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="apiSecret" className="font-medium">API Secret</Label>
                        <div className="flex items-center space-x-2">
                            <Input
                                id="apiSecret"
                                value={apiSecret || ''}
                                readOnly
                                className="font-mono text-sm bg-gray-50"
                            />
                            <Button
                                variant="outline"
                                size="icon"
                                disabled={!apiSecret}
                                onClick={() => copyToClipboard(apiSecret || "")}
                                title="Copy API Secret"
                                className="cursor-default"
                            >
                                <Copy className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>

                </div>

                <DialogFooter className="sm:justify-start text-sm text-gray-500">
                    Do not share these credentials with anyone.
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}