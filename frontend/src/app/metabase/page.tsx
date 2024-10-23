export default function Metabase() {
    return <div className="w-full h-full">
        <iframe src="http://localhost:3000/api/metabase/sso?return_to=/dashboard/11" frameborder="0" width="1280" height="1280" allowtransparency></iframe>
        </div>
}