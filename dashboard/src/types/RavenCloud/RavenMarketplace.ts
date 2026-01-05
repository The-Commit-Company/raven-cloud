
export interface RavenMarketplace{
	name: string
	creation: string
	modified: string
	owner: string
	modified_by: string
	docstatus: 0 | 1 | 2
	parent?: string
	parentfield?: string
	parenttype?: string
	idx?: number
	/**	Title : Data	*/
	title: string
	/**	Image : Attach Image	*/
	image?: string
	/**	Status : Select	*/
	status?: "Draft" | "Published" | "In Review" | "Attention Required" | "Rejected" | "Disabled"
	/**	Description : Small Text	*/
	description: string
	/**	Marketplace Type : Select	*/
	marketplace_type: "" | "Bot" | "Document Notifications" | "Schedule Messages"
	/**	Product Name : Data	*/
	product_name: string
	/**	Is AI Bot? : Check	*/
	is_ai_bot?: 0 | 1
	/**	Long Description : HTML Editor	*/
	long_description?: string
	/**	Bot Data : JSON	*/
	bot_data: any
	/**	Linked Apps : Table - Raven Marketplace Linked App	*/
	linked_apps?: any
	/**	Download Count : Int	*/
	download_count?: number
}