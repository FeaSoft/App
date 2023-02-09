! Description:
! Definition of a finite element mesh.
module m_mesh
    use m_node
    use m_element
    implicit none
    
    private
    public t_mesh, new_mesh
    
    type t_mesh
        integer                      :: n_nodes     ! number of nodes
        integer                      :: n_elements  ! number of elements
        integer                      :: m_space     ! modeling space
        type(t_node),    allocatable :: nodes(:)    ! mesh nodes
        type(t_element), allocatable :: elements(:) ! mesh elements
        integer,         allocatable :: e_counts(:) ! number of elements connected to each node
    contains
        procedure :: count_elements_per_node
        final     :: destructor
    end type
    
    interface new_mesh
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Finite element mesh constructor.
    type(t_mesh) function constructor(n_nodes, n_elements, m_space) result(self)
        integer, intent(in) :: n_nodes    ! number of nodes
        integer, intent(in) :: n_elements ! number of elements
        integer, intent(in) :: m_space    ! modeling space
        self%n_nodes    = n_nodes
        self%n_elements = n_elements
        self%m_space    = m_space
        allocate(self%nodes(self%n_nodes))
        allocate(self%elements(self%n_elements))
        allocate(self%e_counts(self%n_nodes))
    end function
    
    ! Description:
    ! Finite element mesh destructor.
    subroutine destructor(self)
        type(t_mesh), intent(inout) :: self
        if (allocated(self%nodes))    deallocate(self%nodes)
        if (allocated(self%elements)) deallocate(self%elements)
        if (allocated(self%e_counts)) deallocate(self%e_counts)
    end subroutine
    
    ! Description:
    ! Counts the number of elements connected to each node.
    subroutine count_elements_per_node(self)
        class(t_mesh), intent(inout) :: self
        integer :: i, j
        
        ! count elements per node
        do i = 1, self%n_elements
            do j = 1, self%elements(i)%n_nodes
                self%e_counts(self%elements(i)%i_nodes(j)) = self%e_counts(self%elements(i)%i_nodes(j)) + 1
            end do
        end do
    end subroutine
    
end module
