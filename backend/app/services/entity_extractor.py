from typing import List, Tuple, Dict, Any
from app.models.event import Event
from app.schemas.entity import ExtractedEntity


class EntityExtractor:
    """Extracts atomic security entities and relationship tuples from normalized events."""

    @staticmethod
    def extract_entities(event: Event) -> List[ExtractedEntity]:
        entities: List[ExtractedEntity] = []

        if event.user_identity:
            user_val = event.user_identity
            uid = user_val if user_val.startswith("user:") else f"user:{user_val}"
            entities.append(ExtractedEntity(
                id=uid,
                entity_type="USER",
                value=user_val,
                role="actor"
            ))

        if event.host:
            host_val = event.host
            hid = host_val if host_val.startswith("host:") else f"host:{host_val}"
            entities.append(ExtractedEntity(
                id=hid,
                entity_type="HOST",
                value=host_val,
                role="endpoint"
            ))

        if event.source_ip:
            ip_val = event.source_ip
            ipid = ip_val if ip_val.startswith("ip:") else f"ip:{ip_val}"
            entities.append(ExtractedEntity(
                id=ipid,
                entity_type="IP",
                value=ip_val,
                role="source"
            ))

        if event.destination_ip:
            dst_val = event.destination_ip
            dst_id = dst_val if dst_val.startswith("ip:") else f"ip:{dst_val}"
            entities.append(ExtractedEntity(
                id=dst_id,
                entity_type="IP",
                value=dst_val,
                role="target"
            ))

        if event.domain:
            dom_val = event.domain
            dom_id = dom_val if dom_val.startswith("domain:") else f"domain:{dom_val}"
            entities.append(ExtractedEntity(
                id=dom_id,
                entity_type="DOMAIN",
                value=dom_val,
                role="network_target"
            ))

        if event.url:
            url_val = event.url
            url_id = url_val if url_val.startswith("url:") else f"url:{url_val}"
            entities.append(ExtractedEntity(
                id=url_id,
                entity_type="URL",
                value=url_val,
                role="web_resource"
            ))

        if event.process_name:
            proc_id = f"proc:{event.host or 'local'}:{event.process_name}"
            entities.append(ExtractedEntity(
                id=proc_id,
                entity_type="PROCESS",
                value=event.process_name,
                role="execution"
            ))

        if event.parent_process:
            parent_id = f"proc:{event.host or 'local'}:{event.parent_process}"
            entities.append(ExtractedEntity(
                id=parent_id,
                entity_type="PROCESS",
                value=event.parent_process,
                role="parent_execution"
            ))

        if event.file_path:
            fpath = event.file_path
            fid = fpath if fpath.startswith("file:") else f"file:{fpath}"
            entities.append(ExtractedEntity(
                id=fid,
                entity_type="FILE",
                value=fpath,
                role="file_system"
            ))

        if event.file_hash:
            hval = event.file_hash
            hid = hval if hval.startswith("hash:") else f"hash:{hval}"
            entities.append(ExtractedEntity(
                id=hid,
                entity_type="HASH",
                value=hval,
                role="fingerprint"
            ))

        if event.resource_id:
            rval = event.resource_id
            rid = rval if rval.startswith("res:") else f"res:{rval}"
            entities.append(ExtractedEntity(
                id=rid,
                entity_type="RESOURCE",
                value=rval,
                role="cloud_asset"
            ))

        return entities

    @staticmethod
    def extract_relationships(event: Event) -> List[Tuple[str, str, str, Dict[str, Any]]]:
        relationships: List[Tuple[str, str, str, Dict[str, Any]]] = []
        base_props = {
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.id,
            "action": event.action,
            "severity": event.severity
        }

        user_id = f"user:{event.user_identity}" if event.user_identity else None
        host_id = f"host:{event.host}" if event.host else None
        src_ip_id = f"ip:{event.source_ip}" if event.source_ip else None
        dst_ip_id = f"ip:{event.destination_ip}" if event.destination_ip else None
        proc_id = f"proc:{event.host or 'local'}:{event.process_name}" if event.process_name else None
        parent_proc_id = f"proc:{event.host or 'local'}:{event.parent_process}" if event.parent_process else None
        file_id = f"file:{event.file_path}" if event.file_path else None
        domain_id = f"domain:{event.domain}" if event.domain else None
        res_id = (event.resource_id if event.resource_id.startswith("res:") else f"res:{event.resource_id}") if event.resource_id else None

        if user_id and src_ip_id:
            relationships.append((user_id, src_ip_id, "LOGGED_FROM_IP", base_props))

        if user_id and host_id:
            relationships.append((user_id, host_id, "ACCESSED_HOST", base_props))

        if user_id and res_id:
            relationships.append((user_id, res_id, "ACCESSED_RESOURCE", base_props))

        if host_id and proc_id:
            relationships.append((host_id, proc_id, "EXECUTED_PROCESS", base_props))

        if parent_proc_id and proc_id and parent_proc_id != proc_id:
            relationships.append((parent_proc_id, proc_id, "PARENT_OF", base_props))

        if proc_id and file_id:
            relationships.append((proc_id, file_id, "ACCESSED_FILE", base_props))

        if host_id and dst_ip_id:
            relationships.append((host_id, dst_ip_id, "CONNECTED_TO_IP", base_props))

        if proc_id and dst_ip_id:
            relationships.append((proc_id, dst_ip_id, "CONNECTED_TO_IP", base_props))

        if dst_ip_id and domain_id:
            relationships.append((dst_ip_id, domain_id, "RESOLVES_TO_DOMAIN", base_props))

        return relationships


entity_extractor = EntityExtractor()
