import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input, Textarea } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { componentsApi } from '../services/apiPhase1';
import { componentRiskSuggestionsApi, SuggestionSetOut, SuggestedHazardOut, SuggestedHarmOut, SuggestedControlOut, SuggestedVerificationMethodOut } from '../services/componentRiskSuggestionsApi';
import { hazardLibraryApi, harmLibraryApi, riskControlLibraryApi, verificationLibraryApi } from '../services/riskKnowledgeBaseApi';
import type { Component } from '../types';

type LibraryLinkType = 'hazard' | 'harm' | 'control' | 'verification';

interface LinkToExistingState {
  type: LibraryLinkType;
  suggestedId: string;
  suggestedText: string;
  libraryList: { id: string; name: string }[];
  loading: boolean;
  search: string;
}

export interface AcceptModalForm {
  failure_mode: string;
  hazard: string;
  hazard_library_id: string | null;
  hazardous_situation: string;
  harm: string;
  harm_library_id: string | null;
  controls: { control_text: string; risk_control_library_id: string | null }[];
  verifications: { verification_text: string; verification_library_id: string | null }[];
}

interface AcceptLinkPickerState {
  type: LibraryLinkType;
  index?: number;
  libraryList: { id: string; name: string }[];
  loading: boolean;
  search: string;
}

const SECTION_ORDER = [
  { key: 'failure_modes', label: 'Suggested Failure Modes', formKey: 'failure_mode' },
  { key: 'hazards', label: 'Suggested Hazards', formKey: 'hazard' },
  { key: 'hazardous_situations', label: 'Suggested Hazardous Situations', formKey: 'hazardous_situation' },
  { key: 'harms', label: 'Suggested Harms', formKey: 'harm' },
  { key: 'controls', label: 'Suggested Controls', formKey: 'control' },
  { key: 'verification_methods', label: 'Suggested Verification Methods', formKey: 'verification' },
] as const;

function getSectionItems(set: SuggestionSetOut, key: (typeof SECTION_ORDER)[number]['key']) {
  const arr = set[key];
  if (!Array.isArray(arr)) return [];
  return arr.map((x: { text?: string }) => x?.text ?? '').filter(Boolean);
}

function getSectionText(set: SuggestionSetOut, key: (typeof SECTION_ORDER)[number]['key']): string {
  return getSectionItems(set, key).join('\n');
}

export default function ComponentDetailPage() {
  const { projectId, componentId } = useParams<{ projectId: string; componentId: string }>();
  const navigate = useNavigate();
  const [component, setComponent] = useState<Component | null>(null);
  const [suggestions, setSuggestions] = useState<SuggestionSetOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [editSet, setEditSet] = useState<SuggestionSetOut | null>(null);
  const [editForm, setEditForm] = useState<Record<string, string>>({});
  const [acceptingId, setAcceptingId] = useState<string | null>(null);
  const [rejectingId, setRejectingId] = useState<string | null>(null);
  const [linkModal, setLinkModal] = useState<LinkToExistingState | null>(null);
  const [linkingId, setLinkingId] = useState<string | null>(null);
  const [acceptModalSet, setAcceptModalSet] = useState<SuggestionSetOut | null>(null);
  const [acceptModalForm, setAcceptModalForm] = useState<AcceptModalForm | null>(null);
  const [acceptLinkPicker, setAcceptLinkPicker] = useState<AcceptLinkPickerState | null>(null);

  const loadComponent = useCallback(async () => {
    if (!projectId) return;
    const list = await componentsApi.getByProject(projectId);
    const c = list.find((x) => x.id === componentId);
    setComponent(c ?? null);
  }, [projectId, componentId]);

  const loadSuggestions = useCallback(async () => {
    if (!projectId || !componentId) return;
    try {
      const list = await componentRiskSuggestionsApi.list(projectId, componentId);
      setSuggestions(list);
    } catch (e) {
      console.error(e);
      setSuggestions([]);
    }
  }, [projectId, componentId]);

  useEffect(() => {
    if (!projectId || !componentId) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        await loadComponent();
        if (!cancelled) await loadSuggestions();
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [projectId, componentId, loadComponent, loadSuggestions]);

  const handleGenerate = async () => {
    if (!projectId || !componentId) return;
    setGenerating(true);
    try {
      await componentRiskSuggestionsApi.generate(projectId, componentId, { regenerate: true });
      await loadSuggestions();
    } catch (e) {
      console.error(e);
      alert('Failed to generate suggestions');
    } finally {
      setGenerating(false);
    }
  };

  const openEdit = (set: SuggestionSetOut) => {
    setEditSet(set);
    setEditForm({
      failure_mode: getSectionText(set, 'failure_modes'),
      hazard: getSectionText(set, 'hazards'),
      hazardous_situation: getSectionText(set, 'hazardous_situations'),
      harm: getSectionText(set, 'harms'),
      control: getSectionText(set, 'controls'),
      verification: getSectionText(set, 'verification_methods'),
    });
  };

  function initAcceptFormFromSet(
    set: SuggestionSetOut,
    textOverrides?: Record<string, string>
  ): AcceptModalForm {
    const hazards = (set.hazards || []) as SuggestedHazardOut[];
    const harms = (set.harms || []) as SuggestedHarmOut[];
    const controls = (set.controls || []) as SuggestedControlOut[];
    const verification_methods = (set.verification_methods || []) as SuggestedVerificationMethodOut[];
    return {
      failure_mode: textOverrides?.failure_mode ?? getSectionText(set, 'failure_modes'),
      hazard: textOverrides?.hazard ?? getSectionText(set, 'hazards'),
      hazard_library_id: hazards[0]?.hazard_library_id ?? null,
      hazardous_situation: textOverrides?.hazardous_situation ?? getSectionText(set, 'hazardous_situations'),
      harm: textOverrides?.harm ?? getSectionText(set, 'harms'),
      harm_library_id: harms[0]?.harm_library_id ?? null,
      controls: controls.length
        ? controls.map((c) => ({ control_text: c.text ?? '', risk_control_library_id: c.risk_control_library_id ?? null }))
        : [{ control_text: textOverrides?.control ?? '', risk_control_library_id: null }],
      verifications: verification_methods.length
        ? verification_methods.map((v) => ({ verification_text: v.text ?? '', verification_library_id: v.verification_library_id ?? null }))
        : [{ verification_text: textOverrides?.verification ?? '', verification_library_id: null }],
    };
  }

  const openAcceptModal = (set: SuggestionSetOut, textOverrides?: Record<string, string>) => {
    setAcceptModalSet(set);
    setAcceptModalForm(initAcceptFormFromSet(set, textOverrides));
  };

  const closeAcceptModal = () => {
    setAcceptModalSet(null);
    setAcceptModalForm(null);
    setAcceptLinkPicker(null);
  };

  const openAcceptLinkPicker = async (type: LibraryLinkType, index?: number) => {
    setAcceptLinkPicker({ type, index, libraryList: [], loading: true, search: '' });
    try {
      let list: { id: string; name: string }[] = [];
      if (type === 'hazard') {
        const arr = await hazardLibraryApi.list({ limit: 500 });
        list = arr.map((x) => ({ id: x.id, name: x.hazard_name || x.id }));
      } else if (type === 'harm') {
        const arr = await harmLibraryApi.list({ limit: 500 });
        list = arr.map((x) => ({ id: x.id, name: x.harm_name || x.id }));
      } else if (type === 'control') {
        const arr = await riskControlLibraryApi.list({ limit: 500 });
        list = arr.map((x) => ({ id: x.id, name: x.control_name || x.id }));
      } else {
        const arr = await verificationLibraryApi.list({ limit: 500 });
        list = arr.map((x) => ({ id: x.id, name: x.verification_method || x.id }));
      }
      setAcceptLinkPicker((p) => (p ? { ...p, libraryList: list, loading: false } : null));
    } catch (e) {
      console.error(e);
      setAcceptLinkPicker((p) => (p ? { ...p, loading: false, libraryList: [] } : null));
    }
  };

  const handleAcceptLinkPickerSelect = (libraryId: string) => {
    if (!acceptModalForm) return;
    const picker = acceptLinkPicker;
    setAcceptLinkPicker(null);
    if (!picker) return;
    if (picker.type === 'hazard') {
      setAcceptModalForm((f) => (f ? { ...f, hazard_library_id: libraryId } : null));
    } else if (picker.type === 'harm') {
      setAcceptModalForm((f) => (f ? { ...f, harm_library_id: libraryId } : null));
    } else if (picker.type === 'control' && picker.index !== undefined) {
      setAcceptModalForm((f) => {
        if (!f) return null;
        const next = [...f.controls];
        next[picker.index!] = { ...next[picker.index!], risk_control_library_id: libraryId };
        return { ...f, controls: next };
      });
    } else if (picker.type === 'verification' && picker.index !== undefined) {
      setAcceptModalForm((f) => {
        if (!f) return null;
        const next = [...f.verifications];
        next[picker.index!] = { ...next[picker.index!], verification_library_id: libraryId };
        return { ...f, verifications: next };
      });
    }
  };

  const handleAcceptModalCreateAndLink = async (type: LibraryLinkType, suggestedId: string) => {
    if (!projectId || !componentId || !acceptModalSet) return;
    setLinkingId(suggestedId);
    try {
      if (type === 'hazard') {
        await componentRiskSuggestionsApi.createAndLinkHazard(projectId, componentId, suggestedId);
      } else if (type === 'harm') {
        await componentRiskSuggestionsApi.createAndLinkHarm(projectId, componentId, suggestedId);
      } else if (type === 'control') {
        await componentRiskSuggestionsApi.createAndLinkControl(projectId, componentId, suggestedId);
      } else {
        await componentRiskSuggestionsApi.createAndLinkVerification(projectId, componentId, suggestedId);
      }
      const refreshed = await componentRiskSuggestionsApi.list(projectId, componentId);
      const nextSet = refreshed.find((s) => s.id === acceptModalSet.id);
      if (nextSet) setAcceptModalForm(initAcceptFormFromSet(nextSet));
    } catch (e) {
      console.error(e);
      alert('Failed to create library entry and link');
    } finally {
      setLinkingId(null);
    }
  };

  const handleAcceptModalSubmit = async () => {
    if (!projectId || !componentId || !acceptModalSet || !acceptModalForm) return;
    setAcceptingId(acceptModalSet.id);
    try {
      const payload = {
        failure_mode: acceptModalForm.failure_mode || undefined,
        hazard: acceptModalForm.hazard || undefined,
        hazardous_situation: acceptModalForm.hazardous_situation || undefined,
        harm: acceptModalForm.harm || undefined,
        control: acceptModalForm.controls.map((c) => c.control_text).filter(Boolean).join('\n') || undefined,
        verification: acceptModalForm.verifications.map((v) => v.verification_text).filter(Boolean).join('\n') || undefined,
        hazard_library_id: acceptModalForm.hazard_library_id ?? undefined,
        harm_library_id: acceptModalForm.harm_library_id ?? undefined,
        controls: acceptModalForm.controls.map((c) => ({
          control_text: c.control_text,
          risk_control_library_id: c.risk_control_library_id ?? undefined,
        })),
        verifications: acceptModalForm.verifications.map((v) => ({
          verification_text: v.verification_text,
          verification_library_id: v.verification_library_id ?? undefined,
        })),
      };
      const { risk_item_id } = await componentRiskSuggestionsApi.accept(
        projectId,
        componentId,
        acceptModalSet.id,
        payload
      );
      closeAcceptModal();
      setEditSet(null);
      await loadSuggestions();
      if (risk_item_id) navigate(`/projects/${projectId}/risk-items/${risk_item_id}`);
    } catch (e) {
      console.error(e);
      alert('Failed to accept suggestion');
    } finally {
      setAcceptingId(null);
    }
  };

  const handleReject = async (set: SuggestionSetOut) => {
    if (!projectId || !componentId) return;
    if (!window.confirm('Remove this suggestion set?')) return;
    setRejectingId(set.id);
    try {
      await componentRiskSuggestionsApi.reject(projectId, componentId, set.id);
      if (editSet?.id === set.id) setEditSet(null);
      await loadSuggestions();
    } catch (e) {
      console.error(e);
      alert('Failed to remove suggestion');
    } finally {
      setRejectingId(null);
    }
  };

  const openLinkToExisting = async (
    type: LibraryLinkType,
    suggestedId: string,
    suggestedText: string
  ) => {
    setLinkModal({
      type,
      suggestedId,
      suggestedText,
      libraryList: [],
      loading: true,
      search: '',
    });
    try {
      let list: { id: string; name: string }[] = [];
      if (type === 'hazard') {
        const arr = await hazardLibraryApi.list({ limit: 500 });
        list = arr.map((x) => ({ id: x.id, name: x.hazard_name || x.id }));
      } else if (type === 'harm') {
        const arr = await harmLibraryApi.list({ limit: 500 });
        list = arr.map((x) => ({ id: x.id, name: x.harm_name || x.id }));
      } else if (type === 'control') {
        const arr = await riskControlLibraryApi.list({ limit: 500 });
        list = arr.map((x) => ({ id: x.id, name: x.control_name || x.id }));
      } else {
        const arr = await verificationLibraryApi.list({ limit: 500 });
        list = arr.map((x) => ({ id: x.id, name: x.verification_method || x.id }));
      }
      setLinkModal((m) => (m ? { ...m, libraryList: list, loading: false } : null));
    } catch (e) {
      console.error(e);
      setLinkModal((m) => (m ? { ...m, loading: false, libraryList: [] } : null));
    }
  };

  const handleLinkToExistingSelect = async (libraryId: string) => {
    if (!projectId || !componentId || !linkModal) return;
    setLinkingId(linkModal.suggestedId);
    try {
      if (linkModal.type === 'hazard') {
        await componentRiskSuggestionsApi.updateHazardLibraryLink(
          projectId,
          componentId,
          linkModal.suggestedId,
          libraryId
        );
      } else if (linkModal.type === 'harm') {
        await componentRiskSuggestionsApi.updateHarmLibraryLink(
          projectId,
          componentId,
          linkModal.suggestedId,
          libraryId
        );
      } else if (linkModal.type === 'control') {
        await componentRiskSuggestionsApi.updateControlLibraryLink(
          projectId,
          componentId,
          linkModal.suggestedId,
          libraryId
        );
      } else {
        await componentRiskSuggestionsApi.updateVerificationLibraryLink(
          projectId,
          componentId,
          linkModal.suggestedId,
          libraryId
        );
      }
      setLinkModal(null);
      await loadSuggestions();
    } catch (e) {
      console.error(e);
      alert('Failed to link to library');
    } finally {
      setLinkingId(null);
    }
  };

  const handleCreateAndLink = async (
    type: LibraryLinkType,
    suggestedId: string
  ) => {
    if (!projectId || !componentId) return;
    setLinkingId(suggestedId);
    try {
      if (type === 'hazard') {
        await componentRiskSuggestionsApi.createAndLinkHazard(projectId, componentId, suggestedId);
      } else if (type === 'harm') {
        await componentRiskSuggestionsApi.createAndLinkHarm(projectId, componentId, suggestedId);
      } else if (type === 'control') {
        await componentRiskSuggestionsApi.createAndLinkControl(projectId, componentId, suggestedId);
      } else {
        await componentRiskSuggestionsApi.createAndLinkVerification(
          projectId,
          componentId,
          suggestedId
        );
      }
      await loadSuggestions();
    } catch (e) {
      console.error(e);
      alert('Failed to create library entry and link');
    } finally {
      setLinkingId(null);
    }
  };

  const handleMakeProjectSpecific = async (
    type: LibraryLinkType,
    suggestedId: string
  ) => {
    if (!projectId || !componentId) return;
    setLinkingId(suggestedId);
    try {
      if (type === 'hazard') {
        await componentRiskSuggestionsApi.updateHazardLibraryLink(
          projectId,
          componentId,
          suggestedId,
          null
        );
      } else if (type === 'harm') {
        await componentRiskSuggestionsApi.updateHarmLibraryLink(
          projectId,
          componentId,
          suggestedId,
          null
        );
      } else if (type === 'control') {
        await componentRiskSuggestionsApi.updateControlLibraryLink(
          projectId,
          componentId,
          suggestedId,
          null
        );
      } else {
        await componentRiskSuggestionsApi.updateVerificationLibraryLink(
          projectId,
          componentId,
          suggestedId,
          null
        );
      }
      await loadSuggestions();
    } catch (e) {
      console.error(e);
      alert('Failed to make project-specific');
    } finally {
      setLinkingId(null);
    }
  };

  if (!projectId || !componentId) {
    return (
      <div className="p-4">
        <p>Missing project or component.</p>
        <Button onClick={() => navigate('/projects')}>Back to projects</Button>
      </div>
    );
  }

  if (loading && !component) {
    return <div className="p-4">Loading...</div>;
  }

  if (!component) {
    return (
      <div className="p-4">
        <p>Component not found.</p>
        <Button onClick={() => navigate(`/projects/${projectId}/dashboard`)}>Back to project</Button>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <PageHeader
        title={component.name}
        subtitle="Component risk suggestions"
      />
      {component.description && (
        <p className="text-sm text-gray-600 mb-4">{component.description}</p>
      )}
      <div className="flex gap-2 mb-6">
        <Button onClick={() => navigate(`/projects/${projectId}/dashboard`)} variant="secondary">
          Back to project
        </Button>
        <Button onClick={handleGenerate} disabled={generating}>
          {generating ? 'Generating…' : 'Generate Risk Suggestions'}
        </Button>
      </div>

      {suggestions.length === 0 && !generating && (
        <Card className="p-6 text-center text-gray-500">
          No suggestions yet. Click &quot;Generate Risk Suggestions&quot; to create them from active rules.
        </Card>
      )}

      {suggestions.map((set) => (
        <Card key={set.id} className="p-4 mb-4">
          <div className="flex justify-between items-start gap-2 mb-3">
            <span className="text-xs text-gray-500">Suggestion set · rule {set.rule_id.slice(0, 8)}</span>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="secondary"
                onClick={() => openEdit(set)}
              >
                Edit
              </Button>
              <Button
                size="sm"
                onClick={() => (editSet?.id === set.id ? openAcceptModal(set, editForm) : openAcceptModal(set))}
                disabled={acceptingId !== null}
              >
                {acceptingId === set.id ? 'Accepting…' : 'Accept'}
              </Button>
              <Button
                size="sm"
                variant="danger"
                onClick={() => handleReject(set)}
                disabled={rejectingId !== null}
              >
                {rejectingId === set.id ? 'Removing…' : 'Reject'}
              </Button>
            </div>
          </div>

          {SECTION_ORDER.map(({ key, label }) => {
            if (key === 'failure_modes' || key === 'hazardous_situations') {
              const items = getSectionItems(set, key);
              if (items.length === 0) return null;
              return (
                <div key={key} className="mb-3">
                  <h4 className="text-sm font-semibold text-gray-700 mb-1">{label}</h4>
                  <ul className="list-disc list-inside text-sm text-gray-800 space-y-0.5">
                    {items.map((text, i) => (
                      <li key={i}>{text}</li>
                    ))}
                  </ul>
                </div>
              );
            }
            if (key === 'hazards') {
              const items = (set.hazards || []) as SuggestedHazardOut[];
              if (items.length === 0) return null;
              return (
                <div key={key} className="mb-3">
                  <h4 className="text-sm font-semibold text-gray-700 mb-1">{label}</h4>
                  <ul className="text-sm text-gray-800 space-y-2">
                    {items.map((item) => (
                      <li key={item.id} className="flex flex-wrap items-center gap-2">
                        <span className="flex-1 min-w-0">{item.text || '—'}</span>
                        <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
                          {item.hazard_library_id ? 'Linked' : 'Project-specific'}
                        </span>
                        <div className="flex gap-1 flex-shrink-0">
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => openLinkToExisting('hazard', item.id, item.text || '')}
                            disabled={!!linkingId}
                          >
                            Link to existing
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleCreateAndLink('hazard', item.id)}
                            disabled={linkingId !== null}
                          >
                            {linkingId === item.id ? 'Creating…' : 'Create new entry'}
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleMakeProjectSpecific('hazard', item.id)}
                            disabled={!!linkingId}
                          >
                            Make project-specific
                          </Button>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            }
            if (key === 'harms') {
              const items = (set.harms || []) as SuggestedHarmOut[];
              if (items.length === 0) return null;
              return (
                <div key={key} className="mb-3">
                  <h4 className="text-sm font-semibold text-gray-700 mb-1">{label}</h4>
                  <ul className="text-sm text-gray-800 space-y-2">
                    {items.map((item) => (
                      <li key={item.id} className="flex flex-wrap items-center gap-2">
                        <span className="flex-1 min-w-0">{item.text || '—'}</span>
                        <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
                          {item.harm_library_id ? 'Linked' : 'Project-specific'}
                        </span>
                        <div className="flex gap-1 flex-shrink-0">
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => openLinkToExisting('harm', item.id, item.text || '')}
                            disabled={!!linkingId}
                          >
                            Link to existing
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleCreateAndLink('harm', item.id)}
                            disabled={linkingId !== null}
                          >
                            {linkingId === item.id ? 'Creating…' : 'Create new entry'}
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleMakeProjectSpecific('harm', item.id)}
                            disabled={!!linkingId}
                          >
                            Make project-specific
                          </Button>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            }
            if (key === 'controls') {
              const items = (set.controls || []) as SuggestedControlOut[];
              if (items.length === 0) return null;
              return (
                <div key={key} className="mb-3">
                  <h4 className="text-sm font-semibold text-gray-700 mb-1">{label}</h4>
                  <ul className="text-sm text-gray-800 space-y-2">
                    {items.map((item) => (
                      <li key={item.id} className="flex flex-wrap items-center gap-2">
                        <span className="flex-1 min-w-0">{item.text || '—'}</span>
                        <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
                          {item.risk_control_library_id ? 'Linked' : 'Project-specific'}
                        </span>
                        <div className="flex gap-1 flex-shrink-0">
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => openLinkToExisting('control', item.id, item.text || '')}
                            disabled={!!linkingId}
                          >
                            Link to existing
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleCreateAndLink('control', item.id)}
                            disabled={linkingId !== null}
                          >
                            {linkingId === item.id ? 'Creating…' : 'Create new entry'}
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleMakeProjectSpecific('control', item.id)}
                            disabled={!!linkingId}
                          >
                            Make project-specific
                          </Button>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            }
            if (key === 'verification_methods') {
              const items = (set.verification_methods || []) as SuggestedVerificationMethodOut[];
              if (items.length === 0) return null;
              return (
                <div key={key} className="mb-3">
                  <h4 className="text-sm font-semibold text-gray-700 mb-1">{label}</h4>
                  <ul className="text-sm text-gray-800 space-y-2">
                    {items.map((item) => (
                      <li key={item.id} className="flex flex-wrap items-center gap-2">
                        <span className="flex-1 min-w-0">{item.text || '—'}</span>
                        <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
                          {item.verification_library_id ? 'Linked' : 'Project-specific'}
                        </span>
                        <div className="flex gap-1 flex-shrink-0">
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => openLinkToExisting('verification', item.id, item.text || '')}
                            disabled={!!linkingId}
                          >
                            Link to existing
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleCreateAndLink('verification', item.id)}
                            disabled={linkingId !== null}
                          >
                            {linkingId === item.id ? 'Creating…' : 'Create new entry'}
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleMakeProjectSpecific('verification', item.id)}
                            disabled={!!linkingId}
                          >
                            Make project-specific
                          </Button>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            }
            return null;
          })}
        </Card>
      ))}

      <Modal
        isOpen={editSet !== null}
        onClose={() => setEditSet(null)}
        title="Edit suggestion before acceptance"
      >
        {editSet && (
          <div className="space-y-3">
            {SECTION_ORDER.map(({ key, label, formKey }) => (
              <div key={key}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                <Textarea
                  value={editForm[formKey] ?? ''}
                  onChange={(e) => setEditForm((f) => ({ ...f, [formKey]: e.target.value }))}
                  rows={2}
                  className="w-full"
                />
              </div>
            ))}
            <div className="flex gap-2 pt-2">
              <Button onClick={() => { openAcceptModal(editSet, editForm); setEditSet(null); }}>
                Accept with edits
              </Button>
              <Button variant="secondary" onClick={() => setEditSet(null)}>
                Cancel
              </Button>
            </div>
          </div>
        )}
      </Modal>

      <Modal
        isOpen={linkModal !== null}
        onClose={() => setLinkModal(null)}
        title={`Link to existing ${linkModal?.type === 'verification' ? 'verification' : linkModal?.type} library`}
      >
        {linkModal && (
          <div className="space-y-3">
            <p className="text-sm text-gray-600">
              Suggestion: &quot;{linkModal.suggestedText.slice(0, 80)}
              {linkModal.suggestedText.length > 80 ? '…' : ''}&quot;
            </p>
            <Input
              placeholder="Search library..."
              value={linkModal.search}
              onChange={(e) =>
                setLinkModal((m) => (m ? { ...m, search: e.target.value } : null))
              }
              className="w-full"
            />
            {linkModal.loading ? (
              <p className="text-sm text-gray-500">Loading library…</p>
            ) : (
              <ul className="max-h-64 overflow-y-auto border rounded divide-y text-sm">
                {linkModal.libraryList
                  .filter(
                    (x) =>
                      !linkModal.search.trim() ||
                      x.name.toLowerCase().includes(linkModal.search.toLowerCase())
                  )
                  .map((x) => (
                    <li key={x.id}>
                      <button
                        type="button"
                        className="w-full text-left px-3 py-2 hover:bg-gray-100"
                        onClick={() => handleLinkToExistingSelect(x.id)}
                        disabled={linkingId !== null}
                      >
                        {x.name}
                      </button>
                    </li>
                  ))}
              </ul>
            )}
            <div className="flex justify-end">
              <Button variant="secondary" onClick={() => setLinkModal(null)}>
                Cancel
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Accept suggestion modal: map to library / create new / keep project-specific */}
      <Modal
        isOpen={acceptModalSet !== null && acceptModalForm !== null}
        onClose={closeAcceptModal}
        title="Accept suggestion — map to library or keep custom"
        size="lg"
      >
        {acceptModalSet && acceptModalForm && (
          <div className="space-y-4 max-h-[70vh] overflow-y-auto">
            <p className="text-sm text-gray-600">
              Map each item to an existing library entry, create a new one, or keep as project-specific text.
              Manage libraries under <Link to="/libraries/hazards" className="text-primary underline">Libraries</Link> (hazards, harms, risk controls, verifications).
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Failure mode</label>
              <Textarea
                value={acceptModalForm.failure_mode}
                onChange={(e) => setAcceptModalForm((f) => f ? { ...f, failure_mode: e.target.value } : null)}
                rows={1}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hazard</label>
              <Textarea
                value={acceptModalForm.hazard}
                onChange={(e) => setAcceptModalForm((f) => f ? { ...f, hazard: e.target.value } : null)}
                rows={1}
                className="w-full mb-1"
              />
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100">
                  {acceptModalForm.hazard_library_id ? 'Linked to library' : 'Project-specific'}
                </span>
                <Button size="sm" variant="secondary" onClick={() => openAcceptLinkPicker('hazard')} disabled={!!linkingId}>
                  Map to existing
                </Button>
                <Button size="sm" variant="secondary" onClick={() => acceptModalSet.hazards?.[0]?.id && handleAcceptModalCreateAndLink('hazard', acceptModalSet.hazards[0].id)} disabled={!!linkingId}>
                  {linkingId ? 'Creating…' : 'Create new library entry'}
                </Button>
                <Button size="sm" variant="secondary" onClick={() => setAcceptModalForm((f) => f ? { ...f, hazard_library_id: null } : null)}>
                  Keep project-specific
                </Button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hazardous situation</label>
              <Textarea
                value={acceptModalForm.hazardous_situation}
                onChange={(e) => setAcceptModalForm((f) => f ? { ...f, hazardous_situation: e.target.value } : null)}
                rows={2}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Harm</label>
              <Textarea
                value={acceptModalForm.harm}
                onChange={(e) => setAcceptModalForm((f) => f ? { ...f, harm: e.target.value } : null)}
                rows={1}
                className="w-full mb-1"
              />
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100">
                  {acceptModalForm.harm_library_id ? 'Linked to library' : 'Project-specific'}
                </span>
                <Button size="sm" variant="secondary" onClick={() => openAcceptLinkPicker('harm')} disabled={!!linkingId}>
                  Map to existing
                </Button>
                <Button size="sm" variant="secondary" onClick={() => acceptModalSet.harms?.[0]?.id && handleAcceptModalCreateAndLink('harm', acceptModalSet.harms[0].id)} disabled={!!linkingId}>
                  {linkingId ? 'Creating…' : 'Create new library entry'}
                </Button>
                <Button size="sm" variant="secondary" onClick={() => setAcceptModalForm((f) => f ? { ...f, harm_library_id: null } : null)}>
                  Keep project-specific
                </Button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Controls</label>
              {acceptModalForm.controls.map((c, i) => (
                <div key={i} className="mb-2 pl-2 border-l-2 border-gray-200">
                  <Textarea
                    value={c.control_text}
                    onChange={(e) => {
                      setAcceptModalForm((f) => {
                        if (!f) return null;
                        const next = [...f.controls];
                        next[i] = { ...next[i], control_text: e.target.value };
                        return { ...f, controls: next };
                      });
                    }}
                    rows={1}
                    className="w-full mb-1"
                  />
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100">
                      {c.risk_control_library_id ? 'Linked' : 'Project-specific'}
                    </span>
                    <Button size="sm" variant="secondary" onClick={() => openAcceptLinkPicker('control', i)} disabled={!!linkingId}>
                      Map to existing
                    </Button>
                    <Button size="sm" variant="secondary" onClick={() => acceptModalSet.controls?.[i]?.id && handleAcceptModalCreateAndLink('control', acceptModalSet.controls[i].id)} disabled={!!linkingId}>
                      {linkingId ? 'Creating…' : 'Create new'}
                    </Button>
                    <Button size="sm" variant="secondary" onClick={() => setAcceptModalForm((f) => {
                      if (!f) return null;
                      const next = [...f.controls];
                      next[i] = { ...next[i], risk_control_library_id: null };
                      return { ...f, controls: next };
                    })}>
                      Project-specific
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Verifications</label>
              {acceptModalForm.verifications.map((v, i) => (
                <div key={i} className="mb-2 pl-2 border-l-2 border-gray-200">
                  <Textarea
                    value={v.verification_text}
                    onChange={(e) => {
                      setAcceptModalForm((f) => {
                        if (!f) return null;
                        const next = [...f.verifications];
                        next[i] = { ...next[i], verification_text: e.target.value };
                        return { ...f, verifications: next };
                      });
                    }}
                    rows={1}
                    className="w-full mb-1"
                  />
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100">
                      {v.verification_library_id ? 'Linked' : 'Project-specific'}
                    </span>
                    <Button size="sm" variant="secondary" onClick={() => openAcceptLinkPicker('verification', i)} disabled={!!linkingId}>
                      Map to existing
                    </Button>
                    <Button size="sm" variant="secondary" onClick={() => acceptModalSet.verification_methods?.[i]?.id && handleAcceptModalCreateAndLink('verification', acceptModalSet.verification_methods[i].id)} disabled={!!linkingId}>
                      {linkingId ? 'Creating…' : 'Create new'}
                    </Button>
                    <Button size="sm" variant="secondary" onClick={() => setAcceptModalForm((f) => {
                      if (!f) return null;
                      const next = [...f.verifications];
                      next[i] = { ...next[i], verification_library_id: null };
                      return { ...f, verifications: next };
                    })}>
                      Project-specific
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t">
              <Button variant="secondary" onClick={closeAcceptModal}>Cancel</Button>
              <Button onClick={handleAcceptModalSubmit} disabled={!!acceptingId}>
                {acceptingId ? 'Accepting…' : 'Accept'}
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Link picker used inside Accept modal */}
      <Modal
        isOpen={acceptLinkPicker !== null}
        onClose={() => setAcceptLinkPicker(null)}
        title={`Select ${acceptLinkPicker?.type === 'verification' ? 'verification' : acceptLinkPicker?.type} from library`}
      >
        {acceptLinkPicker && (
          <div className="space-y-3">
            <Input
              placeholder="Search..."
              value={acceptLinkPicker.search}
              onChange={(e) => setAcceptLinkPicker((p) => (p ? { ...p, search: e.target.value } : null))}
              className="w-full"
            />
            {acceptLinkPicker.loading ? (
              <p className="text-sm text-gray-500">Loading…</p>
            ) : (
              <ul className="max-h-64 overflow-y-auto border rounded divide-y text-sm">
                {acceptLinkPicker.libraryList
                  .filter((x) => !acceptLinkPicker.search.trim() || x.name.toLowerCase().includes(acceptLinkPicker.search.toLowerCase()))
                  .map((x) => (
                    <li key={x.id}>
                      <button
                        type="button"
                        className="w-full text-left px-3 py-2 hover:bg-gray-100"
                        onClick={() => handleAcceptLinkPickerSelect(x.id)}
                      >
                        {x.name}
                      </button>
                    </li>
                  ))}
              </ul>
            )}
            <div className="flex justify-end">
              <Button variant="secondary" onClick={() => setAcceptLinkPicker(null)}>Cancel</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
