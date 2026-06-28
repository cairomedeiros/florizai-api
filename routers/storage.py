from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from ..config.supabase import get_supabase, get_supabase_admin
from ..config.settings import settings

router = APIRouter()
SIGNED_TTL = 3600  # 1h


@router.get("/{path:path}")
def signed_redirect(path: str):
    # ponytail: route is NOT auth-gated, so <Image> (which can't send a bearer
    # header) loads the file directly. Privacy rests on unguessable UUID paths +
    # 1h signed-URL expiry, not per-user auth. If image privacy ever needs to be
    # stricter, switch to returning signed URLs inside the authed plant payload.
    try:
        client = get_supabase_admin()  # service key signs private-bucket paths
    except RuntimeError:
        client = get_supabase()
    res = client.storage.from_("leafchat").create_signed_url(path, SIGNED_TTL)
    url = res.get("signedURL") or res.get("signedUrl")
    if not url:
        raise HTTPException(status_code=404, detail="Could not sign storage path.")
    if url.startswith("/"):  # older supabase-py returns a relative path
        url = settings.SUPABASE_URL.rstrip("/") + url
    return RedirectResponse(url)
