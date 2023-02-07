! Description:
! Global finite element procedures.
module m_gproc
    use linear_algebra
    use data_model
    use m_eproc
    implicit none
    
    private
    public g_get_K, g_get_F, g_get_Ub, g_add_Pc
    
    contains
    
    ! Description:
    ! Computes the global stiffness matrix, Kaa and Kab.
    subroutine g_get_K(n_adofs, n_idofs, mesh, sections, materials, Kaa, Kab)
        ! procedure arguments
        integer,          intent(in)  :: n_adofs      ! number of active degrees of freedom
        integer,          intent(in)  :: n_idofs      ! number of inactive degrees of freedom
        type(t_mesh),     intent(in)  :: mesh         ! finite element mesh
        type(t_section),  intent(in)  :: sections(:)  ! sections
        type(t_material), intent(in)  :: materials(:) ! materials
        type(t_sparse),   intent(out) :: Kaa, Kab     ! global stiffness matrix
        
        ! additional variables
        type(t_matrix), allocatable :: Ks(:)    ! element stiffness matrices
        type(t_element)             :: element  ! finite element
        type(t_section)             :: section  ! element section
        type(t_material)            :: material ! section material
        integer                     :: i        ! loop counter
        
        ! compute element stiffness matrices first (giving a chance for this loop to be parallelized)
        allocate(Ks(mesh%n_elements))
        do i = 1, mesh%n_elements
            element  = mesh%elements(i)
            section  = sections(element%i_section)
            material = materials(section%i_material)
            Ks(i)    = e_get_K(element, section, material, mesh%nodes)
        end do
        
        ! build global matrix
        call local_to_global_matrix(n_adofs, n_idofs, mesh%n_elements, mesh%elements, Ks, Kaa, Kab)
        
        ! deallocate Ks
        if (allocated(Ks)) deallocate(Ks)
    end subroutine
    
    ! Description:
    ! Computes the global internal forces vector, F.
    ! Also computes strains and stress at the integration points.
    subroutine g_get_F(n_adofs, n_idofs, mesh, sections, materials, Ua, Ub, Fa, Fb, strain, stress)
        ! procedure arguments
        integer,          intent(in)    :: n_adofs      ! number of active degrees of freedom
        integer,          intent(in)    :: n_idofs      ! number of inactive degrees of freedom
        type(t_mesh),     intent(in)    :: mesh         ! finite element mesh
        type(t_section),  intent(in)    :: sections(:)  ! sections
        type(t_material), intent(in)    :: materials(:) ! materials
        type(t_vector),   intent(in)    :: Ua, Ub       ! nodal displacements (global)
        type(t_vector),   intent(out)   :: Fa, Fb       ! global internal forces vector
        type(t_matrix),   intent(inout) :: strain(:)    ! strain at the integration points
        type(t_matrix),   intent(inout) :: stress(:)    ! stress at the integration points
        
        ! additional variables
        type(t_vector), allocatable :: Fs(:)    ! element internal forces vectors
        type(t_element)             :: element  ! finite element
        type(t_section)             :: section  ! element section
        type(t_material)            :: material ! section material
        integer                     :: i        ! loop counter
        
        ! compute element internal forces vectors first (giving a chance for this loop to be parallelized)
        allocate(Fs(mesh%n_elements))
        do i = 1, mesh%n_elements
            element  = mesh%elements(i)
            section  = sections(element%i_section)
            material = materials(section%i_material)
            Fs(i)   = e_get_F(element, section, material, mesh%nodes, Ua, Ub, strain(i), stress(i))
        end do
        
        ! build global vector
        call local_to_global_vector(n_adofs, n_idofs, mesh%n_elements, mesh%elements, Fs, Fa, Fb)
        
        ! deallocate Fs
        if (allocated(Fs)) deallocate(Fs)
    end subroutine
    
    ! Description:
    ! Returns the known displacements vector, Ub.
    type(t_vector) function g_get_Ub(m_space, n_idofs, n_boundaries, nodes, boundaries, nsets) result(Ub)
        ! procedure arguments
        integer,          intent(in) :: m_space       ! modeling space
        integer,          intent(in) :: n_idofs       ! number of inactive degrees of freedom
        integer,          intent(in) :: n_boundaries  ! number of boundary conditions
        type(t_node),     intent(in) :: nodes(:)      ! mesh nodes
        type(t_boundary), intent(in) :: boundaries(:) ! boundary conditions
        type(t_nset),     intent(in) :: nsets(:)      ! node sets
        
        ! additional variables
        type(t_boundary) :: boundary ! boundary condition
        type(t_nset)     :: nset     ! node set
        type(t_node)     :: node     ! mesh node
        integer          :: i, j, k  ! loop counters
        
        ! initialize vector
        Ub = new_vector(n_idofs)
        
        ! build vector
        do i = 1, n_boundaries
            boundary = boundaries(i)
            nset     = nsets(boundary%i_nset)
            do j = 1, nset%n_nodes
                node = nodes(nset%i_nodes(j))
                do k = 1, m_space
                    if (node%dofs(k) < 0) then
                        Ub%at(abs(node%dofs(k))) = boundary%components(k)
                    end if
                end do
            end do
        end do
    end function
    
    ! Description:
    ! Adds the global concentrated loads vector, Pc, to the equivalent nodal loads vector, Pa.
    subroutine g_add_Pc(m_space, n_cloads, nodes, cloads, nsets, Pa)
        ! procedure arguments
        integer,        intent(in)    :: m_space   ! modeling space
        integer,        intent(in)    :: n_cloads  ! number of concentrated loads
        type(t_node),   intent(in)    :: nodes(:)  ! mesh nodes
        type(t_cload),  intent(in)    :: cloads(:) ! concentrated loads
        type(t_nset),   intent(in)    :: nsets(:)  ! node sets
        type(t_vector), intent(inout) :: Pa        ! equivalent nodal loads vector
        
        ! additional variables
        type(t_cload) :: cload   ! concentrated load
        type(t_nset)  :: nset    ! node set
        type(t_node)  :: node    ! mesh node
        integer       :: i, j, k ! loop counters
        
        ! add contributions to vector
        do i = 1, n_cloads
            cload = cloads(i)
            nset  = nsets(cload%i_nset)
            do j = 1, nset%n_nodes
                node = nodes(nset%i_nodes(j))
                do k = 1, m_space
                    if (node%dofs(k) > 0) then
                        Pa%at(node%dofs(k)) = Pa%at(node%dofs(k)) + cload%components(k)
                    end if
                end do
            end do
        end do
    end subroutine
    
    ! Description:
    ! Builds a global system matrix based on the specified element matrices.
    subroutine local_to_global_matrix(n_adofs, n_idofs, n_elements, elements, As, Aaa, Aab)
        ! procedure arguments
        integer,         intent(in)  :: n_adofs     ! number of active degrees of freedom
        integer,         intent(in)  :: n_idofs     ! number of inactive degrees of freedom
        integer,         intent(in)  :: n_elements  ! number of elements
        type(t_element), intent(in)  :: elements(:) ! mesh elements
        type(t_matrix),  intent(in)  :: As(:)       ! the element matrices
        type(t_sparse),  intent(out) :: Aaa, Aab    ! the global matrix
        
        ! additional variables
        integer :: il, jl ! local indices
        integer :: ig, jg ! global indices
        integer :: k      ! element index
        
        ! initialize global sparse matrices
        Aaa = new_sparse(n_adofs, n_adofs)
        Aab = new_sparse(n_adofs, n_idofs)
        
        ! local to global
        do k = 1, n_elements
            do il = 1, elements(k)%n_edofs
                ig = elements(k)%dofs(il)
                if (ig > 0) then
                    do jl = 1, elements(k)%n_edofs
                        jg = elements(k)%dofs(jl)
                        if (jg > 0) then
                            call Aaa%add(ig, jg, As(k)%at(il, jl))
                        else
                            call Aab%add(ig, abs(jg), As(k)%at(il, jl))
                        end if
                    end do
                end if
            end do
        end do
        
        ! use compact storage
        call Aaa%to_csr()
        call Aab%to_csr()
    end subroutine
    
    ! Description:
    ! Builds a global system vector based on the specified element vectors.
    subroutine local_to_global_vector(n_adofs, n_idofs, n_elements, elements, Vs, Vaa, Vab)
        ! procedure arguments
        integer,         intent(in)  :: n_adofs     ! number of active degrees of freedom
        integer,         intent(in)  :: n_idofs     ! number of inactive degrees of freedom
        integer,         intent(in)  :: n_elements  ! number of elements
        type(t_element), intent(in)  :: elements(:) ! mesh elements
        type(t_vector),  intent(in)  :: Vs(:)       ! the element vectors
        type(t_vector),  intent(out) :: Vaa, Vab    ! the global vector
        
        ! additional variables
        integer :: il ! local index
        integer :: ig ! global index
        integer :: k  ! element index
        
        ! initialize global vectors
        Vaa = new_vector(n_adofs)
        Vab = new_vector(n_idofs)
        
        ! local to global
        do k = 1, n_elements
            do il = 1, elements(k)%n_edofs
                ig = elements(k)%dofs(il)
                if (ig > 0) then
                    Vaa%at(ig) = Vaa%at(ig) + Vs(k)%at(il)
                else
                    Vab%at(ig) = Vab%at(ig) + Vs(k)%at(abs(il))
                end if
            end do
        end do
        
    end subroutine
    
end module
